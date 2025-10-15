from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4

app = FastAPI()

class Story(BaseModel):
    id: str
    title: str
    content: str

stories_db: List[Story]= []

@app.post("/stories")
def create_story(story: Story):
    story.id = str(uuid4())
    stories_db.append(story)
    return story

@app.get("/stories")
def get_all_stories():
    return stories_db

@app.get("/stories/{story_id}")
def get_story(story_id: str):
    for s in stories_db:
        if s.id == story_id:
            return s
        raise HTTPException(status_code=404,detail="story not found")
    
@app.put("/stories/{story_id}")
def replace_story(story_id: str,new_story: Story):
    for i, s in enumerate(stories_db):
        if s.id == story_id:
            new_story.id = story_id
            stories_db[i] = new_story
            return new_story
        raise HTTPException(status_code=404,detail="story not found")
    
@app.patch("/stories/{story_id}")
def patch_story(story_id: str,update: dict):
    for i, s in enumerate(stories_db):
        if s.id == story_id:
            data = s.dict()
            data.update(update)
            stories_db[i]= Story(**data)
            return stories_db[i]
        raise HTTPException(status_code=404,detail="story not found")

@app.delete("/stories/{story_id}")
def delete_story(story_id: str):
    for i, s in enumerate(stories_db):
        if s.id == story_id:
            stories_db.pop(i)
            return {"message": "Story deleted"}
        raise HTTPException(status_code=404,detail="story not found")