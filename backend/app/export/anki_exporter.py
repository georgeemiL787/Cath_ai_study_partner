"""
Anki Export Module for AI Study Partner
Handles exporting flashcards to Anki-compatible format
"""

import genanki
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class Flashcard:
    """Flashcard structure"""
    front: str
    back: str
    tags: List[str] = None
    deck_name: str = "AI Study Partner"

class AnkiExporter:
    """Export flashcards to Anki format"""
    
    def __init__(self, deck_name: str = "AI Study Partner"):
        self.deck_name = deck_name
        self.logger = logging.getLogger(__name__)
        
        # Create Anki deck
        self.deck_id = 2059400110  # Random ID for the deck
        self.deck = genanki.Deck(self.deck_id, self.deck_name)
        
        # Define card model
        self.model_id = 1091735104  # Random ID for the model
        self.model = genanki.Model(
            self.model_id,
            'AI Study Partner Card',
            fields=[
                {'name': 'Front'},
                {'name': 'Back'},
                {'name': 'Tags'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Back}}<br><br><small>{{Tags}}</small>',
                },
            ],
            css='''
            .card {
                font-family: Arial, sans-serif;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
            .front {
                font-weight: bold;
                margin-bottom: 20px;
            }
            .back {
                margin-top: 20px;
                padding: 10px;
                background-color: #f0f0f0;
                border-radius: 5px;
            }
            '''
        )
        
    def add_flashcard(self, flashcard: Flashcard):
        """Add a flashcard to the deck"""
        note = genanki.Note(
            model=self.model,
            fields=[
                flashcard.front,
                flashcard.back,
                ', '.join(flashcard.tags) if flashcard.tags else ''
            ]
        )
        self.deck.add_note(note)
        
    def add_flashcards(self, flashcards: List[Flashcard]):
        """Add multiple flashcards to the deck"""
        for flashcard in flashcards:
            self.add_flashcard(flashcard)
            
    def export_to_file(self, filename: str) -> str:
        """Export deck to .apkg file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            # Generate package
            package = genanki.Package(self.deck)
            package.write_to_file(filename)
            
            self.logger.info(f"Anki deck exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export Anki deck: {e}")
            raise
            
    def export_to_bytes(self) -> bytes:
        """Export deck to bytes"""
        try:
            package = genanki.Package(self.deck)
            return package.write_to_bytes()
            
        except Exception as e:
            self.logger.error(f"Failed to export Anki deck to bytes: {e}")
            raise
            
    def parse_flashcard_text(self, text: str) -> List[Flashcard]:
        """Parse flashcard text into structured format"""
        flashcards = []
        lines = text.strip().split('\n')
        
        current_front = None
        current_back = []
        current_tags = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Front:') or line.startswith('Q:'):
                # Save previous card if exists
                if current_front and current_back:
                    flashcards.append(Flashcard(
                        front=current_front,
                        back=' '.join(current_back),
                        tags=current_tags.copy()
                    ))
                
                # Start new card
                current_front = line.split(':', 1)[1].strip()
                current_back = []
                current_tags = []
                
            elif line.startswith('Back:') or line.startswith('A:'):
                if current_front:
                    current_back.append(line.split(':', 1)[1].strip())
                    
            elif line.startswith('Tags:'):
                if current_front:
                    tags_text = line.split(':', 1)[1].strip()
                    current_tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                    
            elif line and current_front:
                # Continuation of back content
                current_back.append(line)
                
        # Add last card
        if current_front and current_back:
            flashcards.append(Flashcard(
                front=current_front,
                back=' '.join(current_back),
                tags=current_tags.copy()
            ))
            
        return flashcards
        
    def create_from_content(self, content: str, tags: List[str] = None) -> 'AnkiExporter':
        """Create exporter from content string"""
        flashcards = self.parse_flashcard_text(content)
        
        for flashcard in flashcards:
            if tags:
                flashcard.tags.extend(tags)
            self.add_flashcard(flashcard)
            
        return self
        
    def get_deck_info(self) -> Dict[str, Any]:
        """Get information about the current deck"""
        return {
            "deck_name": self.deck_name,
            "deck_id": self.deck_id,
            "card_count": len(self.deck.notes),
            "model_id": self.model_id
        }
        
    def clear_deck(self):
        """Clear all cards from the deck"""
        self.deck = genanki.Deck(self.deck_id, self.deck_name)
        
    @staticmethod
    def create_from_json(json_data: str) -> 'AnkiExporter':
        """Create exporter from JSON data"""
        try:
            data = json.loads(json_data)
            deck_name = data.get('deck_name', 'AI Study Partner')
            exporter = AnkiExporter(deck_name)
            
            flashcards_data = data.get('flashcards', [])
            for card_data in flashcards_data:
                flashcard = Flashcard(
                    front=card_data.get('front', ''),
                    back=card_data.get('back', ''),
                    tags=card_data.get('tags', [])
                )
                exporter.add_flashcard(flashcard)
                
            return exporter
            
        except Exception as e:
            logging.error(f"Failed to create exporter from JSON: {e}")
            raise
