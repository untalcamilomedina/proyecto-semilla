from typing import List, Optional, Any, Dict, Literal, Union
from pydantic import BaseModel, Field

# --- FlowSpec (Diagrama de Flujo) ---

class FlowNode(BaseModel):
    id: str
    type: Literal["start", "process", "decision", "end"]
    label: str
    meta: Dict[str, Any] = Field(default_factory=dict)

class FlowEdge(BaseModel):
    id: str
    source: str = Field(..., alias="from")
    target: str = Field(..., alias="to")
    label: Optional[str] = ""
    meta: Dict[str, Any] = Field(default_factory=dict)

class FlowLayoutPosition(BaseModel):
    x: float
    y: float

class FlowLayout(BaseModel):
    engine: Literal["elk", "dagre", "manual"]
    positions: Dict[str, FlowLayoutPosition]

class FlowSpec(BaseModel):
    nodes: List[FlowNode]
    edges: List[FlowEdge]
    layout: Optional[FlowLayout] = None

# --- ERDSpec (Entidad-Relación) ---

class ERDAttribute(BaseModel):
    name: str
    type: str  # text, uuid, integer, boolean, etc.
    pk: bool = False
    unique: bool = False
    nullable: bool = True

class ERDEntity(BaseModel):
    id: str
    name: str
    attributes: List[ERDAttribute]

class ERDForeignKeyResult(BaseModel):
    fromAttribute: str
    toAttribute: str

class ERDRelationship(BaseModel):
    id: str
    source: str = Field(..., alias="from")
    target: str = Field(..., alias="to")
    cardinality: Literal["1:1", "1:N", "N:M"]
    fk: Optional[ERDForeignKeyResult] = None

class ERDSpec(BaseModel):
    entities: List[ERDEntity]
    relationships: List[ERDRelationship]
    notes: List[str] = Field(default_factory=list)
