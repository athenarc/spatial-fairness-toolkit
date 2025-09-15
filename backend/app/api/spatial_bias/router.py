# src/api/endpoints.py

from fastapi import APIRouter
from .models import (
    AuditRequest,
    AuditResponse,
    RelabelingRequest,
    ThresholdAdjustmentRequest,
    RelabelingResponse,
    ThresholdAdjustmentResponse,
)
from .audit_logic import (
    run_audit_pipeline,
)

from .relabel_logic import (
    run_relabel_mitigation,
)

from .threshold_logic import (
    run_threshold_mitigation,
)

router = APIRouter()


@router.post("/audit", response_model=AuditResponse)
def audit_endpoint(req: AuditRequest):
    return run_audit_pipeline(req)


@router.post("/mitigate/relabel", response_model=RelabelingResponse)
def relabel_endpoint(req: RelabelingRequest):
    return run_relabel_mitigation(req)


@router.post("/mitigate/threshold", response_model=ThresholdAdjustmentResponse)
def threshold_adjustment_endpoint(req: ThresholdAdjustmentRequest):
    return run_threshold_mitigation(req)
