from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'document'
    document_id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)

    full_versions = relationship('DocumentFullVersion', back_populates='document')

class DocumentFullVersion(Base):
    __tablename__ = 'document_full_version'
    document_full_version_id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('document.document_id'), nullable=False)
    content = Column(Text, nullable=False)
    acquisition_datetime = Column(DateTime, default=datetime.now)

    document = relationship('Document', back_populates='full_versions')
    diffs = relationship('DocumentDiff', back_populates='full_version')
    summary = relationship('Summary', back_populates='full_version', uselist=False)
    files = relationship('File', back_populates='full_version')

class DocumentDiff(Base):
    __tablename__ = 'document_diff'
    document_diff_id = Column(Integer, primary_key=True)
    document_full_version_id = Column(Integer, ForeignKey('document_full_version.document_full_version_id'), nullable=False)
    content = Column(Text, nullable=False)
    datetime = Column(DateTime, default=datetime.now)

    full_version = relationship('DocumentFullVersion', back_populates='diffs')
    summary_diffs = relationship('SummaryDiff', back_populates='document_diff')

class Summary(Base):
    __tablename__ = 'summary'
    summary_id = Column(Integer, primary_key=True)
    document_full_version_id = Column(Integer, ForeignKey('document_full_version.document_full_version_id'), nullable=False)
    content = Column(Text, nullable=False)
    datetime = Column(DateTime, default=datetime.now)

    full_version = relationship('DocumentFullVersion', back_populates='summary')
    summary_diffs = relationship('SummaryDiff', back_populates='summary')

class SummaryDiff(Base):
    __tablename__ = 'summary_diff'
    summary_diff_id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey('summary.summary_id'), nullable=False)
    document_diff_id = Column(Integer, ForeignKey('document_diff.document_diff_id'), nullable=False)

    summary = relationship('Summary', back_populates='summary_diffs')
    document_diff = relationship('DocumentDiff', back_populates='summary_diffs')

class File(Base):
    __tablename__ = 'file'
    file_id = Column(Integer, primary_key=True)
    document_full_version_id = Column(Integer, ForeignKey('document_full_version.document_full_version_id'), nullable=False)
    blob = Column(LargeBinary, nullable=True)  # zakładam Text; możesz zmienić na LargeBinary jeśli potrzeba
    url = Column(String, nullable=True)

    full_version = relationship('DocumentFullVersion', back_populates='files')

