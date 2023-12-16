from sqlalchemy import Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Mobil(Base):
    __tablename__ = 'mobil'
    id_mobil: Mapped[int] = mapped_column(primary_key=True)
    harga: Mapped[int] = mapped_column()
    thn_produksi: Mapped[int] = mapped_column()
    kekuatan_mesin: Mapped[int] = mapped_column()
    konsumsi_bhn_bakar: Mapped[int] = mapped_column()  
    
    def __repr__(self) -> str:
        return f"mobil(id_mobil={self.id_mobil!r}, harga={self.harga!r})"
