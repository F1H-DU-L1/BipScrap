from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DocumentFull(Base):
    __tablename__ = 'document_full'
    doc_id = Column(Integer, primary_key=True)
    base_URL = Column(String, nullable=False)
    scrap_datetime = Column(DateTime, default=datetime.now)
    URL = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    diffs_as_first = relationship('DocumentDiff', foreign_keys='DocumentDiff.doc_id_key_1', back_populates='doc1')
    diffs_as_second = relationship('DocumentDiff', foreign_keys='DocumentDiff.doc_id_key_2', back_populates='doc2')


class DocumentDiff(Base):
    __tablename__ = 'document_diff'
    doc_diff_id = Column(Integer, primary_key=True)
    doc_id_key_1 = Column(Integer, ForeignKey('document_full.doc_id'), nullable=False)
    doc_id_key_2 = Column(Integer, ForeignKey('document_full.doc_id'), nullable=True)
    content = Column(Text, nullable=False)

    doc1 = relationship('DocumentFull', foreign_keys=[doc_id_key_1], back_populates='diffs_as_first')
    doc2 = relationship('DocumentFull', foreign_keys=[doc_id_key_2], back_populates='diffs_as_second')

    llm_outputs = relationship('LLM', back_populates='diff')


class LLM(Base):
    __tablename__ = 'llm'
    LLM_id = Column(Integer, primary_key=True)
    doc_diff_id = Column(Integer, ForeignKey('document_diff.doc_diff_id'), nullable=False)
    base_URL = Column(String, nullable=False)
    date_time = Column(DateTime, default=datetime.now)
    content = Column(Text, nullable=False)

    diff = relationship('DocumentDiff', back_populates='llm_outputs')
    
    
                        

