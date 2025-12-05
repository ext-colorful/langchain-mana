"""Agent API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...agents.runtime import AgentContext, agent_runtime
from ...core.database import get_db
from ...core.security import get_current_user
from ...schemas.agent import (
    AgentCreate,
    AgentListResponse,
    AgentResponse,
    AgentRunRequest,
    AgentRunResponse,
    AgentUpdate,
)
from ...storage.models import Agent
from ...utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/create", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new agent"""
    try:
        # Create agent
        new_agent = Agent(
            user_id=current_user["user_id"],
            name=agent_data.name,
            description=agent_data.description,
            model_provider=agent_data.model_provider,
            model_name=agent_data.model_name,
            temperature=agent_data.temperature,
            max_tokens=agent_data.max_tokens,
            system_prompt=agent_data.system_prompt,
            tools=agent_data.tools,
            rag_enabled=agent_data.rag_enabled,
            knowledge_base_ids=agent_data.knowledge_base_ids,
            max_iterations=agent_data.max_iterations,
            routing_strategy=agent_data.routing_strategy.value
        )
        
        db.add(new_agent)
        await db.commit()
        await db.refresh(new_agent)
        
        logger.info(f"Agent created: {new_agent.id} by user {current_user['user_id']}")
        return new_agent
    
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=AgentListResponse)
async def list_agents(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's agents"""
    try:
        # Query agents
        stmt = select(Agent).where(
            Agent.user_id == current_user["user_id"]
        ).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        agents = result.scalars().all()
        
        # Count total
        count_stmt = select(Agent).where(Agent.user_id == current_user["user_id"])
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        return AgentListResponse(total=total, agents=agents)
    
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get agent by ID"""
    try:
        stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update agent configuration"""
    try:
        stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update fields
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        await db.commit()
        await db.refresh(agent)
        
        logger.info(f"Agent updated: {agent_id}")
        return agent
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete agent"""
    try:
        stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        await db.delete(agent)
        await db.commit()
        
        logger.info(f"Agent deleted: {agent_id}")
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent(
    agent_id: int,
    request: AgentRunRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run agent with a message"""
    try:
        # Get agent
        stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user["user_id"]
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if not agent.is_active:
            raise HTTPException(status_code=400, detail="Agent is not active")
        
        # Build agent config
        agent_config = {
            "id": agent.id,
            "model_provider": agent.model_provider,
            "model_name": agent.model_name,
            "temperature": agent.temperature,
            "max_tokens": agent.max_tokens,
            "system_prompt": agent.system_prompt,
            "tools": agent.tools,
            "rag_enabled": agent.rag_enabled,
            "knowledge_base_ids": agent.knowledge_base_ids,
            "max_iterations": agent.max_iterations,
            "routing_strategy": agent.routing_strategy
        }
        
        # Create context
        context = AgentContext(
            agent_config=agent_config,
            session_id=request.session_id,
            user_id=current_user["user_id"]
        )
        
        # Run agent
        result = await agent_runtime.run(context, request.message)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Agent execution failed"))
        
        return AgentRunResponse(
            session_id=request.session_id or 0,
            message_id=0,  # TODO: Save to database
            response=result["response"],
            metadata=result["metadata"],
            latency_ms=result["metadata"].get("latency_ms")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to run agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
