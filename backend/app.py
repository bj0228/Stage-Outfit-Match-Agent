import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent.outfit_agent import OutfitAgent
from agent.report_generator import ReportGenerator
from llm.llm_client import LLMClient

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"

app = FastAPI(title="Stage Outfit Match Agent", version="1.0.0")

origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OutfitRequest(BaseModel):
    dance_input: str = Field(..., min_length=2, description="舞蹈题目或视频链接")
    style: str = Field("甜美", description="目标风格")
    budget: str = Field("中预算", description="预算偏好")


@app.get("/")
async def root() -> dict:
    return {"name": "Stage Outfit Match Agent", "docs": "/docs"}


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "provider": os.getenv("LLM_PROVIDER", "mock")}


@app.post("/api/outfit")
async def create_outfit_plan(request: OutfitRequest) -> dict:
    try:
        logger.info("Creating outfit plan for style=%s budget=%s", request.style, request.budget)
        llm = LLMClient()
        agent = OutfitAgent(llm)
        result = await agent.run(request.dance_input, request.style, request.budget)

        report_generator = ReportGenerator(str(REPORTS_DIR))
        report_id, _ = report_generator.create(request.model_dump(), result)
        result["report_id"] = report_id
        result["logs"].append("已生成 PDF 搭配报告")
        return result
    except Exception as exc:
        logger.exception("Outfit agent failed")
        raise HTTPException(status_code=500, detail=f"智能体运行失败：{exc}") from exc


@app.get("/api/report/{report_id}")
async def download_report(report_id: str) -> FileResponse:
    safe_name = os.path.basename(report_id)
    path = REPORTS_DIR / safe_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="报告不存在")
    return FileResponse(path, media_type="application/pdf", filename=safe_name)
