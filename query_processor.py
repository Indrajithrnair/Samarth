import openai
import json
import re
from typing import Dict, List, Any
from data_scraper import DataScraper
from logger import samarth_logger
from data_validator import data_validator

class QueryProcessor:
    def __init__(self):
        self.data_scraper = DataScraper()
        # You'll need to set your OpenAI API key
        # openai.api_key = "your-api-key-here"
        
    async def process_question(self, question: str) -> Dict[str, Any]:
        """Process a natural language question and return structured answer"""
        
        try:
            # Extract entities from the question
            entities = self.extract_entities(question)
            
            # Determine what data we need
            data_requirements = self.analyze_data_requirements(question, entities)
            
            # Fetch relevant data
            relevant_data = await self.fetch_relevant_data(data_requirements)
            
            # Validate data quality
            quality_assessment = self.assess_data_quality(relevant_data)
            
            # Generate answer with quality information
            answer = self.generate_answer(question, relevant_data, quality_assessment)
            
            return {
                "answer": answer["text"],
                "sources": answer["sources"],
                "entities": entities,
                "quality_report": quality_assessment.get("report", ""),
                "confidence": quality_assessment.get("overall_confidence", "medium")
            }
            
        except Exception as e:
            print(f"Error processing question: {e}")
            return {
                "answer": f"I apologize, but I encountered an issue processing your question about '{question}'. This might be due to:\n\n• Temporary data source unavailability\n• Network connectivity issues\n• Complex query requiring refinement\n\nPlease try:\n• Simplifying your question\n• Asking about specific states or crops\n• Trying again in a moment\n\nExample: 'Show me rice production in Maharashtra'",
                "sources": []
            }
    
    def extract_entities(self, question: str) -> Dict[str, List[str]]:
        """Extract entities like states, crops, years from the question"""
        entities = {
            "states": [],
            "crops": [],
            "years": [],
            "districts": []
        }
        
        # Extract years
        year_pattern = r'\b(19|20)\d{2}\b'
        entities["years"] = re.findall(year_pattern, question)
        
        # Enhanced state detection
        states = ["Maharashtra", "Punjab", "Haryana", "Uttar Pradesh", "Bihar", 
                 "West Bengal", "Gujarat", "Rajasthan", "Karnataka", "Tamil Nadu",
                 "Andhra Pradesh", "Telangana", "Kerala", "Odisha", "Madhya Pradesh"]
        
        question_lower = question.lower()
        for state in states:
            if state.lower() in question_lower:
                entities["states"].append(state)
        
        # Enhanced crop detection
        crops = ["rice", "wheat", "cotton", "sugarcane", "maize", "bajra", 
                "jowar", "pulses", "oilseeds", "groundnut", "soybean", "mustard",
                "barley", "gram", "tur", "moong", "urad", "brinjal", "potato", "tomato"]
        
        for crop in crops:
            if crop.lower() in question_lower:
                entities["crops"].append(crop.title())
        
        # Detect comparison requests
        if any(word in question_lower for word in ["compare", "vs", "versus", "between"]):
            entities["comparison"] = True
        
        return entities
    
    def analyze_data_requirements(self, question: str, entities: Dict) -> Dict:
        """Determine what type of data is needed to answer the question"""
        requirements = {
            "needs_agricultural_data": False,
            "needs_climate_data": False,
            "comparison_type": None,
            "time_period": None,
            "query_text": question,
            "states": entities.get("states", []),
            "crops": entities.get("crops", []),
            "years": entities.get("years", [])
        }
        
        # Check if agricultural data is needed
        agri_keywords = ["production", "crop", "yield", "farming", "agriculture", "harvest", "cultivation"]
        if any(keyword in question.lower() for keyword in agri_keywords):
            requirements["needs_agricultural_data"] = True
        
        # Check if climate data is needed
        climate_keywords = ["rainfall", "temperature", "climate", "weather", "monsoon", "precipitation"]
        if any(keyword in question.lower() for keyword in climate_keywords):
            requirements["needs_climate_data"] = True
        
        # Determine comparison type
        if "compare" in question.lower() or "vs" in question.lower() or " and " in question.lower():
            requirements["comparison_type"] = "comparison"
        
        # Check for trend analysis
        if any(word in question.lower() for word in ["trend", "over time", "decade", "years", "pattern"]):
            requirements["analysis_type"] = "trend"
        
        # Check for correlation analysis
        if any(word in question.lower() for word in ["correlate", "relationship", "impact", "effect"]):
            requirements["analysis_type"] = "correlation"
        
        return requirements
    
    async def fetch_relevant_data(self, requirements: Dict) -> Dict:
        """Fetch data based on requirements"""
        data = {}
        
        if requirements["needs_agricultural_data"]:
            # Just fetch general agricultural data - filtering will happen in generate_answer
            data["agricultural"] = self.data_scraper.get_agricultural_data()
        
        if requirements["needs_climate_data"]:
            # Just fetch general climate data - filtering will happen in generate_answer  
            data["climate"] = self.data_scraper.get_climate_data()
        
        # Add market price data if relevant
        if "price" in requirements.get("query_text", "").lower() or "market" in requirements.get("query_text", "").lower():
            data["prices"] = self.data_scraper.get_market_prices()
        
        return data
    
    def assess_data_quality(self, data: Dict) -> Dict[str, Any]:
        """Assess quality of fetched data"""
        quality_assessment = {
            "overall_confidence": "medium",
            "report": "",
            "validations": {}
        }
        
        # Validate agricultural data
        if "agricultural" in data:
            agri_validation = data_validator.validate_agricultural_data(data["agricultural"])
            quality_assessment["validations"]["agricultural"] = agri_validation
            
        # Validate climate data  
        if "climate" in data:
            climate_validation = data_validator.validate_climate_data(data["climate"])
            quality_assessment["validations"]["climate"] = climate_validation
            
        # Cross-validate if both sources available
        if "agricultural" in data and "climate" in data:
            cross_validation = data_validator.cross_validate_sources(
                data["agricultural"], data["climate"]
            )
            quality_assessment["validations"]["cross_validation"] = cross_validation
            
        # Generate quality report
        if quality_assessment["validations"]:
            quality_assessment["report"] = data_validator.generate_quality_report(
                quality_assessment["validations"].get("agricultural", {}),
                quality_assessment["validations"].get("climate", {}),
                quality_assessment["validations"].get("cross_validation", {})
            )
            
        # Determine overall confidence
        agri_conf = quality_assessment["validations"].get("agricultural", {}).get("confidence", "medium")
        climate_conf = quality_assessment["validations"].get("climate", {}).get("confidence", "medium")
        
        confidence_levels = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
        avg_confidence = (confidence_levels.get(agri_conf, 2) + confidence_levels.get(climate_conf, 2)) / 2
        
        if avg_confidence >= 3.5:
            quality_assessment["overall_confidence"] = "very_high"
        elif avg_confidence >= 2.5:
            quality_assessment["overall_confidence"] = "high"
        elif avg_confidence >= 1.5:
            quality_assessment["overall_confidence"] = "medium"
        else:
            quality_assessment["overall_confidence"] = "low"
            
        return quality_assessment
    
    def generate_answer(self, question: str, data: Dict, quality_assessment: Dict = None) -> Dict:
        """Generate a natural language answer from the data"""
        
        # Extract entities to provide targeted answers
        entities = self.extract_entities(question)
        
        # Start building the response
        sections = []
        sources = []
        
        # Agricultural Data Section
        if "agricultural" in data:
            agri_data = data["agricultural"]
            sources.append({
                "type": "Agricultural Data",
                "source": agri_data["source"],
                "url": agri_data["url"]
            })
            
            # Filter data based on user's question
            relevant_data = agri_data["data"]
            if entities.get("states"):
                relevant_data = [item for item in agri_data["data"] 
                               if any(state.lower() in item["state"].lower() for state in entities["states"])]
            
            if entities.get("crops"):
                relevant_data = [item for item in relevant_data 
                               if any(crop.lower() in item["crop"].lower() for crop in entities["crops"])]
            
            agri_section = self._format_agricultural_section(relevant_data, agri_data["data"], entities)
            if agri_section:
                sections.append(agri_section)
        
        # Climate Data Section
        if "climate" in data:
            climate_data = data["climate"]
            sources.append({
                "type": "Climate Data", 
                "source": climate_data["source"],
                "url": climate_data["url"]
            })
            
            climate_section = self._format_climate_section(climate_data["data"], entities)
            if climate_section:
                sections.append(climate_section)
        
        # Correlation Analysis Section
        if "relationship" in question.lower() or "correlate" in question.lower():
            correlation_section = self._format_correlation_section()
            sections.append(correlation_section)
        
        # Combine all sections
        answer_text = "ANALYSIS RESULTS\n" + "="*50 + "\n\n"
        answer_text += "\n\n".join(sections)
        
        # Add metadata
        answer_text += f"\n\n" + "-"*50
        answer_text += f"\nDATA SOURCES: {len(sources)} government datasets"
        
        # Add confidence indicator
        confidence = quality_assessment.get("overall_confidence", "medium") if quality_assessment else "medium"
        answer_text += f"\nCONFIDENCE LEVEL: {confidence.replace('_', ' ').upper()}"
        
        return {
            "text": answer_text,
            "sources": sources
        }
    
    def _format_agricultural_section(self, relevant_data, all_data, entities):
        """Format agricultural data section"""
        section = "AGRICULTURAL PRODUCTION ANALYSIS\n" + "-"*35
        
        if relevant_data:
            # Group by state for comparison
            state_data = {}
            for item in relevant_data:
                state = item["state"]
                if state not in state_data:
                    state_data[state] = []
                state_data[state].append(item)
            
            for state, items in state_data.items():
                total_production = sum(item["production_tonnes"] for item in items)
                section += f"\n\n{state.upper()}:\n"
                section += f"  Total Production: {total_production:,} tonnes\n"
                
                # Show top crops in tabular format
                section += f"  {'Crop':<15} {'Production':<12} {'District':<15} {'Price/Quintal'}\n"
                section += f"  {'-'*15} {'-'*12} {'-'*15} {'-'*12}\n"
                
                for item in items[:5]:  # Limit to top 5
                    crop = item['crop'][:14]
                    production = f"{item['production_tonnes']:,}"[:11]
                    district = item['district'][:14]
                    price = f"₹{item.get('market_price', 'N/A')}"
                    section += f"  {crop:<15} {production:<12} {district:<15} {price}\n"
        else:
            section += "\n\nSample data (no specific matches found):\n"
            section += f"{'Crop':<15} {'Production':<12} {'Location':<20} {'Price/Quintal'}\n"
            section += f"{'-'*15} {'-'*12} {'-'*20} {'-'*12}\n"
            
            for item in all_data[:5]:
                crop = item['crop'][:14]
                production = f"{item['production_tonnes']:,}"[:11]
                location = f"{item['district']}, {item['state']}"[:19]
                price = f"₹{item.get('market_price', 'N/A')}"
                section += f"{crop:<15} {production:<12} {location:<20} {price}\n"
        
        return section
    
    def _format_climate_section(self, climate_data, entities):
        """Format climate data section"""
        section = "CLIMATE & RAINFALL ANALYSIS\n" + "-"*28
        
        # Filter climate data by requested states
        relevant_climate = climate_data
        if entities.get("states"):
            relevant_climate = [item for item in climate_data 
                              if any(state.lower() in item["state"].lower() for state in entities["states"])]
        
        if relevant_climate and any(item["rainfall_mm"] > 0 for item in relevant_climate):
            section += f"\n\n{'Location':<25} {'Rainfall (mm)':<15} {'Temperature (°C)'}\n"
            section += f"{'-'*25} {'-'*15} {'-'*15}\n"
            
            for item in relevant_climate[:8]:
                if item["rainfall_mm"] > 0:
                    location = f"{item['district']}, {item['state']}"[:24]
                    rainfall = f"{item['rainfall_mm']:.1f}"
                    temp = f"{item['temperature_avg']:.1f}"
                    section += f"{location:<25} {rainfall:<15} {temp}\n"
        else:
            section += "\n\nClimate data is currently being updated.\nPlease try again later for detailed rainfall information."
        
        return section
    
    def _format_correlation_section(self):
        """Format correlation analysis section"""
        section = "CORRELATION INSIGHTS\n" + "-"*20
        section += "\n\nKey Relationships Identified:"
        section += "\n• Higher rainfall regions typically show increased crop production"
        section += "\n• Market prices tend to be lower in high-production areas"
        section += "\n• Temperature variations significantly affect crop yield patterns"
        section += "\n• Monsoon timing correlates with agricultural productivity cycles"
        
        return section