from fastapi import APIRouter

from app.salesforce.load_contract import build_salesforce_load_plan
from app.salesforce.models import SalesforceLoadPlanRequest, SalesforceLoadPlanResponse

router = APIRouter(prefix="/salesforce", tags=["salesforce"])


@router.post("/load-plan", response_model=SalesforceLoadPlanResponse)
def create_salesforce_load_plan(
    request: SalesforceLoadPlanRequest,
) -> SalesforceLoadPlanResponse:
    return SalesforceLoadPlanResponse(
        load_plan=build_salesforce_load_plan(request.output_columns, request.target)
    )
