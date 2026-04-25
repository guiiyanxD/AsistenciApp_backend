import datetime
from data.repositories.inscripcion_repository import InscripcionRepository


class InscripcionService:

    def __init__(self):
        self.repo = InscripcionRepository()

    def unirse_por_codigo(self, codigo: str, estudiante_id: str) -> dict:
        if not codigo or not codigo.strip():
            raise ValueError("El código de invitación es obligatorio")

        grupo = self.repo.buscar_grupo_por_codigo(codigo.strip().upper())
        if not grupo:
            raise LookupError("Código de invitación inválido o inexistente")

        if not grupo["activo"]:
            raise ValueError("Este grupo ya no está activo")

        if not grupo["periodo_activo"]:
            raise ValueError("El periodo académico de este grupo no está activo")

        fecha_fin = grupo["fecha_fin"]
        if isinstance(fecha_fin, str):
            fecha_fin = datetime.date.fromisoformat(fecha_fin)
        if fecha_fin < datetime.date.today():
            raise ValueError("El periodo académico de este grupo ya finalizó")

        if self.repo.existe_inscripcion(grupo["id"], estudiante_id):
            raise ValueError("Ya estás inscrito en este grupo")

        if grupo["cupo_maximo"] is not None:
            inscritos = self.repo.contar_inscritos(grupo["id"])
            if inscritos >= grupo["cupo_maximo"]:
                raise ValueError("El grupo ha alcanzado su cupo máximo")

        inscripcion = self.repo.crear(grupo["id"], estudiante_id)
        return {
            "inscripcion": inscripcion,
            "grupo": {
                "id": grupo["id"],
                "nombre": grupo["nombre"],
                "materia_nombre": grupo["materia_nombre"],
                "periodo_nombre": grupo["periodo_nombre"],
                "fecha_inicio": str(grupo["fecha_inicio"]),
                "fecha_fin": str(grupo["fecha_fin"]),
            },
        }

    def listar_grupos_estudiante(self, estudiante_id: str) -> list[dict]:
        return self.repo.listar_por_estudiante(estudiante_id)
