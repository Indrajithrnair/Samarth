import json
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class DataValidator:
    """
    Data quality validation and scoring system
    Ensures accuracy and reliability of government data
    """
    
    def __init__(self):
        self.quality_thresholds = {
            "completeness": 0.8,  # 80% of expected fields present
            "consistency": 0.9,   # 90% consistency across sources
            "freshness": 30,      # Data not older than 30 days
            "accuracy": 0.85      # 85% accuracy score
        }
        
    def validate_agricultural_data(self, data: Dict) -> Dict[str, Any]:
        """Validate agricultural production data"""
        validation_result = {
            "is_valid": True,
            "quality_score": 0.0,
            "issues": [],
            "confidence": "high"
        }
        
        if not data.get("data"):
            validation_result["is_valid"] = False
            validation_result["issues"].append("No data records found")
            return validation_result
            
        records = data["data"]
        
        # Check completeness
        completeness_score = self._check_completeness(records, 
            required_fields=["state", "district", "crop", "production_tonnes"])
        
        # Check consistency
        consistency_score = self._check_consistency(records)
        
        # Check for outliers
        outlier_score = self._check_outliers(records, "production_tonnes")
        
        # Check data freshness
        freshness_score = self._check_freshness(data)
        
        # Calculate overall quality score
        validation_result["quality_score"] = (
            completeness_score * 0.3 +
            consistency_score * 0.3 +
            outlier_score * 0.2 +
            freshness_score * 0.2
        )
        
        # Determine confidence level
        if validation_result["quality_score"] >= 0.9:
            validation_result["confidence"] = "very_high"
        elif validation_result["quality_score"] >= 0.8:
            validation_result["confidence"] = "high"
        elif validation_result["quality_score"] >= 0.7:
            validation_result["confidence"] = "medium"
        else:
            validation_result["confidence"] = "low"
            
        return validation_result
        
    def validate_climate_data(self, data: Dict) -> Dict[str, Any]:
        """Validate climate/rainfall data"""
        validation_result = {
            "is_valid": True,
            "quality_score": 0.0,
            "issues": [],
            "confidence": "high"
        }
        
        if not data.get("data"):
            validation_result["is_valid"] = False
            validation_result["issues"].append("No climate data records found")
            return validation_result
            
        records = data["data"]
        
        # Check for reasonable rainfall values (0-5000mm annually)
        rainfall_issues = []
        for record in records:
            rainfall = record.get("rainfall_mm", 0)
            if rainfall < 0 or rainfall > 5000:
                rainfall_issues.append(f"Unusual rainfall: {rainfall}mm in {record.get('district', 'Unknown')}")
                
        if rainfall_issues:
            validation_result["issues"].extend(rainfall_issues)
            
        # Check temperature ranges (5-50°C for India)
        temp_issues = []
        for record in records:
            temp = record.get("temperature_avg", 25)
            if temp < 5 or temp > 50:
                temp_issues.append(f"Unusual temperature: {temp}°C in {record.get('district', 'Unknown')}")
                
        if temp_issues:
            validation_result["issues"].extend(temp_issues)
            
        # Calculate quality score
        completeness_score = self._check_completeness(records, 
            required_fields=["state", "district", "rainfall_mm", "temperature_avg"])
        
        data_quality = 1.0 - (len(rainfall_issues + temp_issues) / max(len(records), 1))
        
        validation_result["quality_score"] = (completeness_score + data_quality) / 2
        
        # Set confidence
        if validation_result["quality_score"] >= 0.8:
            validation_result["confidence"] = "high"
        elif validation_result["quality_score"] >= 0.6:
            validation_result["confidence"] = "medium"
        else:
            validation_result["confidence"] = "low"
            
        return validation_result
        
    def cross_validate_sources(self, agri_data: Dict, climate_data: Dict) -> Dict[str, Any]:
        """Cross-validate data across agricultural and climate sources"""
        validation_result = {
            "correlation_found": False,
            "consistency_score": 0.0,
            "geographic_alignment": 0.0,
            "recommendations": []
        }
        
        if not (agri_data.get("data") and climate_data.get("data")):
            return validation_result
            
        # Check geographic alignment
        agri_states = set(record.get("state", "").lower() for record in agri_data["data"])
        climate_states = set(record.get("state", "").lower() for record in climate_data["data"])
        
        common_states = agri_states.intersection(climate_states)
        total_states = agri_states.union(climate_states)
        
        if total_states:
            validation_result["geographic_alignment"] = len(common_states) / len(total_states)
            
        # Check for logical correlations
        if validation_result["geographic_alignment"] > 0.5:
            validation_result["correlation_found"] = True
            validation_result["recommendations"].append(
                "Strong geographic overlap enables meaningful correlation analysis"
            )
        else:
            validation_result["recommendations"].append(
                "Limited geographic overlap - consider broader data sources"
            )
            
        return validation_result
        
    def _check_completeness(self, records: List[Dict], required_fields: List[str]) -> float:
        """Check data completeness score"""
        if not records:
            return 0.0
            
        total_fields = len(records) * len(required_fields)
        present_fields = 0
        
        for record in records:
            for field in required_fields:
                if record.get(field) is not None and record.get(field) != "":
                    present_fields += 1
                    
        return present_fields / total_fields if total_fields > 0 else 0.0
        
    def _check_consistency(self, records: List[Dict]) -> float:
        """Check data consistency across records"""
        if len(records) < 2:
            return 1.0
            
        # Check for duplicate entries
        seen_combinations = set()
        duplicates = 0
        
        for record in records:
            key = (record.get("state", ""), record.get("district", ""), record.get("crop", ""))
            if key in seen_combinations:
                duplicates += 1
            seen_combinations.add(key)
            
        consistency_score = 1.0 - (duplicates / len(records))
        return max(0.0, consistency_score)
        
    def _check_outliers(self, records: List[Dict], field: str) -> float:
        """Check for statistical outliers in numerical data"""
        values = []
        for record in records:
            value = record.get(field)
            if isinstance(value, (int, float)) and value > 0:
                values.append(value)
                
        if len(values) < 3:
            return 1.0
            
        try:
            mean_val = statistics.mean(values)
            stdev_val = statistics.stdev(values)
            
            outliers = 0
            for value in values:
                if abs(value - mean_val) > 3 * stdev_val:  # 3-sigma rule
                    outliers += 1
                    
            outlier_score = 1.0 - (outliers / len(values))
            return max(0.0, outlier_score)
            
        except statistics.StatisticsError:
            return 1.0
            
    def _check_freshness(self, data: Dict) -> float:
        """Check data freshness based on last update"""
        # For now, assume data is reasonably fresh
        # In production, would check actual timestamps
        source = data.get("source", "")
        if "live" in source.lower() or "real-time" in source.lower():
            return 1.0
        elif "sample" in source.lower():
            return 0.7  # Mock data is less fresh but still useful
        else:
            return 0.8  # Default reasonable freshness
            
    def generate_quality_report(self, agri_validation: Dict, climate_validation: Dict, 
                              cross_validation: Dict) -> str:
        """Generate human-readable quality report"""
        report = "**Data Quality Assessment**\n\n"
        
        # Agricultural data quality
        agri_score = agri_validation.get("quality_score", 0)
        agri_confidence = agri_validation.get("confidence", "unknown")
        report += f"**Agricultural Data**: {agri_score:.1%} quality, {agri_confidence} confidence\n"
        
        if agri_validation.get("issues"):
            report += f"   Issues: {len(agri_validation['issues'])} detected\n"
            
        # Climate data quality
        climate_score = climate_validation.get("quality_score", 0)
        climate_confidence = climate_validation.get("confidence", "unknown")
        report += f"**Climate Data**: {climate_score:.1%} quality, {climate_confidence} confidence\n"
        
        if climate_validation.get("issues"):
            report += f"   Issues: {len(climate_validation['issues'])} detected\n"
            
        # Cross-validation results
        geo_alignment = cross_validation.get("geographic_alignment", 0)
        report += f"**Geographic Alignment**: {geo_alignment:.1%} overlap between sources\n"
        
        # Overall assessment
        overall_score = (agri_score + climate_score) / 2
        if overall_score >= 0.8:
            report += "\n**Overall Assessment**: High quality data suitable for analysis\n"
        elif overall_score >= 0.6:
            report += "\n**Overall Assessment**: Moderate quality, results should be interpreted carefully\n"
        else:
            report += "\n**Overall Assessment**: Low quality data, results may be unreliable\n"
            
        return report

# Global validator instance
data_validator = DataValidator()