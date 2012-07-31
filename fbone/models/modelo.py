#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import *
import datetime


Base = declarative_base()


nodos_profesores = Table("nodos_profesores", Base.metadata,
    Column("id_nodo", Integer, ForeignKey("nodos.id")),
    Column("id_profesor", Integer, ForeignKey("profesores.id")))


proyectos_alumnos = Table("proyectos_alumnos", Base.metadata,
    Column("id_proyecto", Integer, ForeignKey("proyectos.id")),
    Column("id_alumno", Integer, ForeignKey("alumnos.id")))


class Cita(Base):
    __tablename__ = "citas"
    id_proyecto = Column(Integer, ForeignKey("proyectos.id"), primary_key=True)
    id_alumno = Column(Integer, ForeignKey("alumnos.id"), primary_key=True)
    id_sesion = Column(Integer, ForeignKey("sesiones.id"), primary_key=True)
    fecha = Column(DateTime)
    proyecto = relationship("Proyecto", backref="citas")
    alumno = relationship("Alumno", backref="citas")
    sesion = relationship("Sesion", backref="citas")
    
    def __init__(self, fecha):
        self.fecha = fecha
    
    def __str__(self):
        s = "CITA de %s %s en el proyecto %s para el %s\n" % (self.alumno.nombre, self.alumno.apellidos, self.proyecto.nombre, self.fecha)
        return s


class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True)
    #nombre = Column(String(100))
    curso = Column(String(30))
    alumnos = relationship("Alumno", secondary=proyectos_alumnos, backref="proyectos")
    id_nodo = Column(Integer, ForeignKey("nodos.id"))
    citas = relationship("Cita", backref="proyecto")
    
    def __init__(self, nombre, curso):
        self.nombre = nombre
        self.curso = curso
    
    def __str__(self):
        s = "PROYECTO %s (id %d)\n" % (self.curso, self.id)
        for a in self.alumnos:
            s += "\tALUMNO: %s %s (id %d)\n" % (a.nombre, a.apellidos, a.id)
        return s


class Profesor(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    apellidos = Column(String(100))
    foto = Column(String(100))
    
    def __init__(self, nombre, apellidos):
        self.nombre = nombre
        self.apellidos = apellidos
    
    def __str__(self):
        return "PROFESOR %s %s\n" % (self.nombre, self.apellidos)


class Alumno(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50))
    apellidos = Column(String(100))
    password = Column(String(50))
    
    def __init__(self, nombre, apellidos, password=""):
        self.nombre = nombre
        self.apellidos = apellidos
        self.password = password


class Sesion(Base):
    __tablename__ = "sesiones"
    id = Column(Integer, primary_key=True)
    inicio = Column(DateTime)
    fin = Column(DateTime)
    tiempo_bloque = Column(Integer)
    alumnos_bloque = Column(Integer)


class Nodo(Base): # Es la plantilla de titulos, cursos, universidades, etc.
    __tablename__ = "nodos"
    id = Column(Integer, primary_key=True)
    id_padre = Column(Integer, ForeignKey("nodos.id"))
    padre = relationship("Nodo")


def main():
    engine = create_engine("mysql://orlas:orlas@localhost/orlas")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()


if __name__ == "__main__":
    main()
