from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CategoriaDB(Base):
    __tablename__ = "app_categoria"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String, nullable=True)
    productos = relationship("ProductoDB", back_populates="categoria")

class ProductoDB(Base):
    __tablename__ = "app_producto"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(String)
    precio = Column(Float)
    stock = Column(Integer)
    en_venta = Column(Boolean)
    sku = Column(String)
    destacado = Column(Boolean)
    descuento = Column(Integer)
    
    categoria_id = Column(Integer, ForeignKey("app_categoria.id"))
    categoria = relationship("CategoriaDB", back_populates="productos")
