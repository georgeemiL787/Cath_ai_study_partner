"""
CSV Export Module for AI Study Partner
Handles exporting study data to CSV format
"""

import csv
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class CSVExporter:
    """Export study data to CSV format"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def export_flashcards(self, flashcards: List[Dict[str, Any]], filename: str) -> str:
        """Export flashcards to CSV"""
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['front', 'back', 'tags', 'created_at', 'source']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for card in flashcards:
                    writer.writerow({
                        'front': card.get('front', ''),
                        'back': card.get('back', ''),
                        'tags': ', '.join(card.get('tags', [])),
                        'created_at': card.get('created_at', datetime.now().isoformat()),
                        'source': card.get('source', 'AI Study Partner')
                    })
                    
            self.logger.info(f"Flashcards exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export flashcards to CSV: {e}")
            raise
            
    def export_quiz_questions(self, questions: List[Dict[str, Any]], filename: str) -> str:
        """Export quiz questions to CSV"""
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['question', 'type', 'options', 'correct_answer', 'explanation', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for question in questions:
                    options = question.get('options', [])
                    writer.writerow({
                        'question': question.get('question', ''),
                        'type': question.get('type', ''),
                        'options': '|'.join(options) if options else '',
                        'correct_answer': question.get('correct_answer', ''),
                        'explanation': question.get('explanation', ''),
                        'created_at': question.get('created_at', datetime.now().isoformat())
                    })
                    
            self.logger.info(f"Quiz questions exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export quiz questions to CSV: {e}")
            raise
            
    def export_session_data(self, session_data: Dict[str, Any], filename: str) -> str:
        """Export session data to CSV"""
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'content', 'source_type', 'metadata', 'session_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                documents = session_data.get('documents', [])
                for doc in documents:
                    writer.writerow({
                        'timestamp': doc.get('timestamp', ''),
                        'content': doc.get('content', ''),
                        'source_type': doc.get('source_type', ''),
                        'metadata': json.dumps(doc.get('metadata', {})),
                        'session_id': doc.get('session_id', '')
                    })
                    
            self.logger.info(f"Session data exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export session data to CSV: {e}")
            raise
            
    def export_study_plan(self, study_plan: Dict[str, Any], filename: str) -> str:
        """Export study plan to CSV"""
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['topic', 'description', 'estimated_time', 'priority', 'status', 'notes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                topics = study_plan.get('topics', [])
                for topic in topics:
                    writer.writerow({
                        'topic': topic.get('topic', ''),
                        'description': topic.get('description', ''),
                        'estimated_time': topic.get('estimated_time', ''),
                        'priority': topic.get('priority', ''),
                        'status': topic.get('status', 'pending'),
                        'notes': topic.get('notes', '')
                    })
                    
            self.logger.info(f"Study plan exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export study plan to CSV: {e}")
            raise
            
    def export_key_concepts(self, concepts: List[Dict[str, Any]], filename: str) -> str:
        """Export key concepts to CSV"""
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['concept', 'definition', 'importance', 'related_concepts', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for concept in concepts:
                    writer.writerow({
                        'concept': concept.get('concept', ''),
                        'definition': concept.get('definition', ''),
                        'importance': concept.get('importance', ''),
                        'related_concepts': ', '.join(concept.get('related_concepts', [])),
                        'created_at': concept.get('created_at', datetime.now().isoformat())
                    })
                    
            self.logger.info(f"Key concepts exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export key concepts to CSV: {e}")
            raise
            
    def export_comprehensive_report(self, data: Dict[str, Any], filename: str) -> str:
        """Export comprehensive study report to CSV"""
        try:
            os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'type', 'content', 'metadata', 'timestamp', 'session_id', 
                    'source_type', 'confidence', 'processing_time'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                # Export all types of data
                for data_type, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            writer.writerow({
                                'type': data_type,
                                'content': item.get('content', ''),
                                'metadata': json.dumps(item.get('metadata', {})),
                                'timestamp': item.get('timestamp', datetime.now().isoformat()),
                                'session_id': item.get('session_id', ''),
                                'source_type': item.get('source_type', ''),
                                'confidence': item.get('confidence', ''),
                                'processing_time': item.get('processing_time', '')
                            })
                            
            self.logger.info(f"Comprehensive report exported to {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to export comprehensive report to CSV: {e}")
            raise
            
    @staticmethod
    def parse_flashcard_csv(filename: str) -> List[Dict[str, Any]]:
        """Parse flashcards from CSV file"""
        flashcards = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    flashcards.append({
                        'front': row.get('front', ''),
                        'back': row.get('back', ''),
                        'tags': row.get('tags', '').split(', ') if row.get('tags') else [],
                        'created_at': row.get('created_at', ''),
                        'source': row.get('source', '')
                    })
                    
        except Exception as e:
            logging.error(f"Failed to parse flashcard CSV: {e}")
            raise
            
        return flashcards

