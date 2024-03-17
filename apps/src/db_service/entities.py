from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ExperimentOrmModel(Base):
    __tablename__ = "experiment_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_token: Mapped[str]
    button_color: Mapped[str]
    price: Mapped[int]

    _table_args__ = (UniqueConstraint("device_token"),)

    def __str__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.device_token}, {self.button_color}, {self.price})"
        )

    def to_dict(self):
        return {
            key: value
            for key, value in self.__dict__.items()
            if key != "_sa_instance_state"
        }
