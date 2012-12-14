# -*- coding: utf-8 -*-


from octodus.models.types import DenormalizedText

from octodus.models.model import User, Project, Task, Prop 
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata



