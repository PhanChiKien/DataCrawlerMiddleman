from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from database import get_db, init_db, JobPosting, Company, Benefit
from schemas import (
    URLCheckRequest, URLCheckResponse,
    CompanyRequest, CompanyResponse,
    JobPostingRequest, JobPostingResponse,
    BenefitRequest, BenefitResponse,
    DeleteResponse
)
from config import settings

app = FastAPI(title="Crawler Middleware API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "Crawler Middleware API is running"}


# ==================== CHECK ENDPOINT ====================
@app.post("/check", response_model=URLCheckResponse)
def check_url(request: URLCheckRequest, db: Session = Depends(get_db)):
    """
    Check if a URL has already been crawled.
    """
    job = db.query(JobPosting).filter(JobPosting.url == request.url).first()
    
    if job:
        return URLCheckResponse(
            url=request.url,
            is_crawled=True,
            job_id=job.job_id,
            crawled_time=job.crawled_time
        )
    else:
        return URLCheckResponse(
            url=request.url,
            is_crawled=False
        )


# ==================== COMPANY ENDPOINTS ====================
@app.post("/deposit/company", response_model=CompanyResponse)
def deposit_company(request: CompanyRequest, db: Session = Depends(get_db)):
    """
    Deposit a company. If company with same name exists, update it.
    """
    try:
        # Check if company exists by name
        existing = db.query(Company).filter(Company.company_name == request.company_name).first()
        
        if existing:
            # Update existing company
            existing.location = request.location
            existing.description = request.description
            existing.url = request.url
            db.commit()
            db.refresh(existing)
            
            return CompanyResponse(
                company_id=existing.company_id,
                success=True,
                message="Company updated successfully"
            )
        else:
            # Create new company
            new_company = Company(
                company_name=request.company_name,
                location=request.location,
                description=request.description,
                url=request.url
            )
            db.add(new_company)
            db.commit()
            db.refresh(new_company)
            
            return CompanyResponse(
                company_id=new_company.company_id,
                success=True,
                message="Company created successfully"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error depositing company: {str(e)}")


@app.delete("/company/{company_id}", response_model=DeleteResponse)
def delete_company(company_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a company by ID. Also deletes all related job postings and benefits.
    """
    try:
        company = db.query(Company).filter(Company.company_id == company_id).first()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Delete related job postings (and cascade to benefits)
        db.query(JobPosting).filter(JobPosting.company_id == company_id).delete()
        
        # Delete company
        db.delete(company)
        db.commit()
        
        return DeleteResponse(
            success=True,
            message=f"Company and related data deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting company: {str(e)}")


# ==================== JOB POSTING ENDPOINTS ====================
@app.post("/deposit/job", response_model=JobPostingResponse)
def deposit_job(request: JobPostingRequest, db: Session = Depends(get_db)):
    """
    Deposit a job posting. If job with same URL exists, update it.
    """
    try:
        # Verify company exists
        company = db.query(Company).filter(Company.company_id == request.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found. Please create company first.")
        
        # Check if job with same URL exists
        existing = db.query(JobPosting).filter(JobPosting.url == request.url).first()
        
        if existing:
            # Update existing job
            existing.company_id = request.company_id
            existing.job_title = request.job_title
            existing.description = request.description
            existing.salary = request.salary
            existing.pay_period = request.pay_period
            existing.work_type = request.work_type
            existing.experience_level = request.experience_level
            existing.location = request.location
            existing.applies = request.applies
            existing.listed_time = request.listed_time
            existing.currency = request.currency
            existing.platform = request.platform
            existing.crawled_time = datetime.utcnow()
            
            db.commit()
            db.refresh(existing)
            
            return JobPostingResponse(
                job_id=existing.job_id,
                success=True,
                message="Job posting updated successfully",
                crawled_time=existing.crawled_time
            )
        else:
            # Create new job posting
            new_job = JobPosting(
                company_id=request.company_id,
                job_title=request.job_title,
                description=request.description,
                salary=request.salary,
                pay_period=request.pay_period,
                work_type=request.work_type,
                experience_level=request.experience_level,
                location=request.location,
                applies=request.applies,
                listed_time=request.listed_time,
                currency=request.currency,
                platform=request.platform,
                url=request.url
            )
            db.add(new_job)
            db.commit()
            db.refresh(new_job)
            
            return JobPostingResponse(
                job_id=new_job.job_id,
                success=True,
                message="Job posting created successfully",
                crawled_time=new_job.crawled_time
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error depositing job: {str(e)}")


@app.delete("/job/{job_id}", response_model=DeleteResponse)
def delete_job(job_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a job posting by ID. Also deletes all related benefits.
    """
    try:
        job = db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found")
        
        # Delete related benefits
        db.query(Benefit).filter(Benefit.job_id == job_id).delete()
        
        # Delete job
        db.delete(job)
        db.commit()
        
        return DeleteResponse(
            success=True,
            message="Job posting and related benefits deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting job: {str(e)}")


# ==================== BENEFIT ENDPOINTS ====================
@app.post("/deposit/benefit", response_model=BenefitResponse)
def deposit_benefit(request: BenefitRequest, db: Session = Depends(get_db)):
    """
    Deposit a benefit for a job posting.
    """
    try:
        # Verify job exists
        job = db.query(JobPosting).filter(JobPosting.job_id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job posting not found. Please create job first.")
        
        # Create benefit
        new_benefit = Benefit(
            job_id=request.job_id,
            type=request.type,
            inferred=request.inferred
        )
        db.add(new_benefit)
        db.commit()
        db.refresh(new_benefit)
        
        return BenefitResponse(
            benefit_id=new_benefit.id,
            success=True,
            message="Benefit created successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error depositing benefit: {str(e)}")


@app.delete("/benefit/{benefit_id}", response_model=DeleteResponse)
def delete_benefit(benefit_id: int, db: Session = Depends(get_db)):
    """
    Delete a benefit by ID.
    """
    try:
        benefit = db.query(Benefit).filter(Benefit.id == benefit_id).first()
        
        if not benefit:
            raise HTTPException(status_code=404, detail="Benefit not found")
        
        db.delete(benefit)
        db.commit()
        
        return DeleteResponse(
            success=True,
            message="Benefit deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting benefit: {str(e)}")


# ==================== STATS ENDPOINT ====================
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about crawled job postings.
    """
    total_jobs = db.query(JobPosting).count()
    total_companies = db.query(Company).count()
    total_benefits = db.query(Benefit).count()
    
    return {
        "total_job_postings": total_jobs,
        "total_companies": total_companies,
        "total_benefits": total_benefits
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
