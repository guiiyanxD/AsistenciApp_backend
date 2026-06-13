import datetime
from data.repositories.grupo_repository import GrupoRepository
from data.repositories.periodo_repository import PeriodoRepository
from data.repositories.materia_repository import MateriaRepository
from utils.codigo_helper import generar_codigo_invitacion

DIAS_SEMANA = {
    "lunes": 0, "martes": 1, "miercoles": 2,
    "jueves": 3, "viernes": 4, "sabado": 5, "domingo": 6
}

DIAS_VALIDOS = set(DIAS_SEMANA.keys())


class GrupoBusiness:

    def __init__(self):
        self.repo = GrupoRepository()
        self.periodo_repo = PeriodoRepository()
        self.materia_repo = MateriaRepository()

    def crear(self, docente_id: str, periodo_id: str, materia_id: str,
              nombre: str, cupo_maximo: int | None, horarios: list[dict]) -> dict:

        if not nombre or not nombre.strip():
            raise ValueError("El nombre del grupo es obligatorio")
        if not horarios:
            raise ValueError("Debe definir al menos un horario semanal")

        periodo = self.periodo_repo.buscar_por_id(periodo_id, docente_id)
        if not periodo:
            raise LookupError("Periodo académico no encontrado")

        materia = self.materia_repo.buscar_por_id(materia_id, docente_id)
        if not materia:
            raise LookupError("Materia no encontrada")

        self._validar_horarios(horarios)

        codigo = self._generar_codigo_unico()
        grupo = self.repo.crear(periodo_id, materia_id, nombre.strip(), codigo, cupo_maximo)

        horarios_creados = []
        for h in horarios:
            horario = self.repo.agregar_horario(
                grupo["id"], h["dia_semana"], h["hora_inicio"], h["hora_fin"]
            )
            horarios_creados.append(horario)

        clases = self._generar_clases(
            grupo["id"],
            horarios_creados,
            periodo["fecha_inicio"],
            periodo["fecha_fin"],
        )
        self.repo.crear_clases_batch(clases)

        grupo["horarios"] = horarios_creados
        grupo["clases_generadas"] = len(clases)
        return grupo

    def listar(self, docente_id: str) -> list[dict]:
        return self.repo.listar_por_docente(docente_id)

    def obtener(self, grupo_id: str, docente_id: str) -> dict:
        grupo = self.repo.buscar_por_id(grupo_id)
        if not grupo or str(grupo.get("docente_id")) != str(docente_id):
            raise LookupError("Grupo no encontrado")
        grupo["horarios"] = self.repo.listar_horarios(grupo_id)
        return grupo

    def listar_clases(self, grupo_id: str, docente_id: str) -> list[dict]:
        self.obtener(grupo_id, docente_id)
        return self.repo.listar_clases(grupo_id)

    def regenerar_clases(self, grupo_id: str, docente_id: str,
                         nuevos_horarios: list[dict]) -> dict:
        grupo = self.obtener(grupo_id, docente_id)
        self._validar_horarios(nuevos_horarios)

        periodo = self.periodo_repo.buscar_por_id(
            str(grupo["periodo_academico_id"]), docente_id
        )

        self.repo.eliminar_clases_futuras(grupo_id)
        self.repo.eliminar_horarios(grupo_id)

        horarios_creados = []
        for h in nuevos_horarios:
            horario = self.repo.agregar_horario(
                grupo_id, h["dia_semana"], h["hora_inicio"], h["hora_fin"]
            )
            horarios_creados.append(horario)

        clases = self._generar_clases(
            grupo_id,
            horarios_creados,
            periodo["fecha_inicio"],
            periodo["fecha_fin"],
        )
        self.repo.crear_clases_batch(clases)

        return {"horarios": horarios_creados, "clases_regeneradas": len(clases)}

    def _generar_clases(self, grupo_id: str, horarios: list[dict],
                        fecha_inicio, fecha_fin) -> list[dict]:
        if isinstance(fecha_inicio, str):
            fecha_inicio = datetime.date.fromisoformat(str(fecha_inicio))
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.date.fromisoformat(str(fecha_fin))

        mapa_horarios: dict[int, list[dict]] = {}
        for h in horarios:
            numero_dia = DIAS_SEMANA[h["dia_semana"]]
            mapa_horarios.setdefault(numero_dia, []).append(h)

        clases = []
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            dia_numero = fecha_actual.weekday()
            if dia_numero in mapa_horarios:
                for h in mapa_horarios[dia_numero]:
                    clases.append({
                        "grupo_id": grupo_id,
                        "fecha": str(fecha_actual),
                        "hora_inicio": str(h["hora_inicio"]),
                        "hora_fin": str(h["hora_fin"]),
                        "tipo": "clase",
                    })
            fecha_actual += datetime.timedelta(days=1)

        return clases

    def _validar_horarios(self, horarios: list[dict]):
        for h in horarios:
            if h.get("dia_semana") not in DIAS_VALIDOS:
                raise ValueError(f"Día inválido: '{h.get('dia_semana')}'. "
                                 f"Valores permitidos: {', '.join(DIAS_VALIDOS)}")
            if not h.get("hora_inicio") or not h.get("hora_fin"):
                raise ValueError("Cada horario debe tener hora_inicio y hora_fin")
            try:
                hi = datetime.time.fromisoformat(h["hora_inicio"])
                hf = datetime.time.fromisoformat(h["hora_fin"])
            except ValueError:
                raise ValueError("Las horas deben tener formato HH:MM")
            if hf <= hi:
                raise ValueError("La hora de fin debe ser posterior a la hora de inicio")

    def _generar_codigo_unico(self) -> str:
        for _ in range(10):
            codigo = generar_codigo_invitacion()
            return codigo
        raise RuntimeError("No se pudo generar un código de invitación único")
