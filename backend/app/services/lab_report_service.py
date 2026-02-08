"""
Lab Report Analysis Service with AWS Textract OCR integration
"""
import boto3
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from ..config import Config
from ..mongodb.connection import get_mongodb


class LabReportService:
    """Service for lab report analysis and OCR"""
    
    def __init__(self):
        """Initialize AWS Textract client"""
        self.textract_client = None
        self.s3_client = None
        
        # Initialize AWS clients if credentials are available
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            try:
                self.textract_client = boto3.client(
                    'textract',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_REGION
                )
                
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_REGION
                )
                
                print("AWS Textract and S3 clients initialized")
            except Exception as e:
                print(f"Warning: Could not initialize AWS clients: {e}")
        else:
            print("Warning: AWS credentials not configured. Lab report analysis will use mock data.")
    
    def upload_to_s3(self, file_data: bytes, file_name: str, user_id: str) -> str:
        """
        Upload file to S3
        
        Args:
            file_data: File binary data
            file_name: Original file name
            user_id: User ID for organizing files
        
        Returns:
            S3 file path
        """
        if not self.s3_client:
            # Mock upload for development
            return f"mock://lab-reports/{user_id}/{file_name}"
        
        try:
            # Generate unique file path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"lab-reports/{user_id}/{timestamp}_{file_name}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=Config.AWS_S3_BUCKET,
                Key=s3_key,
                Body=file_data,
                ContentType=self._get_content_type(file_name)
            )
            
            return s3_key
            
        except Exception as e:
            raise Exception(f"Error uploading to S3: {str(e)}")
    
    def extract_text_from_file(self, file_path: str, file_data: bytes = None) -> Dict:
        """
        Extract text from lab report using AWS Textract
        
        Args:
            file_path: S3 file path or local path
            file_data: Optional file binary data for direct processing
        
        Returns:
            Dict with extracted text and tables
        """
        if not self.textract_client:
            # Return mock data for development
            return self._get_mock_extraction()
        
        try:
            # Call Textract
            if file_path.startswith('s3://') or file_path.startswith('mock://'):
                # Process from S3
                bucket = Config.AWS_S3_BUCKET
                key = file_path.replace('s3://', '').replace(f'{bucket}/', '')
                
                response = self.textract_client.analyze_document(
                    Document={'S3Object': {'Bucket': bucket, 'Name': key}},
                    FeatureTypes=['TABLES', 'FORMS']
                )
            else:
                # Process from bytes
                response = self.textract_client.analyze_document(
                    Document={'Bytes': file_data},
                    FeatureTypes=['TABLES', 'FORMS']
                )
            
            # Parse Textract response
            extracted_data = self._parse_textract_response(response)
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")
    
    def _parse_textract_response(self, response: Dict) -> Dict:
        """
        Parse Textract API response
        
        Args:
            response: Textract API response
        
        Returns:
            Parsed data with text and tables
        """
        blocks = response.get('Blocks', [])
        
        # Extract text lines
        text_lines = []
        tables = []
        
        for block in blocks:
            if block['BlockType'] == 'LINE':
                text_lines.append(block.get('Text', ''))
            
            elif block['BlockType'] == 'TABLE':
                table_data = self._extract_table(block, blocks)
                if table_data:
                    tables.append(table_data)
        
        return {
            'text_lines': text_lines,
            'tables': tables,
            'full_text': '\n'.join(text_lines)
        }
    
    def _extract_table(self, table_block: Dict, all_blocks: List[Dict]) -> List[List[str]]:
        """
        Extract table data from Textract blocks
        
        Args:
            table_block: Table block from Textract
            all_blocks: All blocks for reference
        
        Returns:
            2D list representing table
        """
        # Create block ID to block mapping
        block_map = {block['Id']: block for block in all_blocks}
        
        # Get table cells
        relationships = table_block.get('Relationships', [])
        cells = []
        
        for relationship in relationships:
            if relationship['Type'] == 'CHILD':
                for cell_id in relationship['Ids']:
                    cell_block = block_map.get(cell_id)
                    if cell_block and cell_block['BlockType'] == 'CELL':
                        cells.append(cell_block)
        
        # Organize cells into rows
        if not cells:
            return []
        
        max_row = max(cell.get('RowIndex', 0) for cell in cells)
        max_col = max(cell.get('ColumnIndex', 0) for cell in cells)
        
        table = [['' for _ in range(max_col)] for _ in range(max_row)]
        
        for cell in cells:
            row_idx = cell.get('RowIndex', 1) - 1
            col_idx = cell.get('ColumnIndex', 1) - 1
            
            # Get cell text
            cell_text = self._get_cell_text(cell, block_map)
            table[row_idx][col_idx] = cell_text
        
        return table
    
    def _get_cell_text(self, cell_block: Dict, block_map: Dict) -> str:
        """Get text content from a cell block"""
        text_parts = []
        
        relationships = cell_block.get('Relationships', [])
        for relationship in relationships:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child_block = block_map.get(child_id)
                    if child_block and child_block['BlockType'] == 'WORD':
                        text_parts.append(child_block.get('Text', ''))
        
        return ' '.join(text_parts)
    
    def parse_lab_values(self, extracted_data: Dict) -> List[Dict]:
        """
        Parse lab values from extracted text
        
        Args:
            extracted_data: Extracted text and tables
        
        Returns:
            List of lab test results
        """
        lab_values = []
        
        # Try to parse from tables first
        for table in extracted_data.get('tables', []):
            lab_values.extend(self._parse_table_for_lab_values(table))
        
        # If no tables, try to parse from text
        if not lab_values:
            lab_values = self._parse_text_for_lab_values(
                extracted_data.get('full_text', '')
            )
        
        return lab_values
    
    def _parse_table_for_lab_values(self, table: List[List[str]]) -> List[Dict]:
        """
        Parse lab values from table data
        
        Args:
            table: 2D list representing table
        
        Returns:
            List of lab test results
        """
        if len(table) < 2:
            return []
        
        lab_values = []
        
        # Assume first row is header
        headers = [h.lower().strip() for h in table[0]]
        
        # Find column indices
        test_col = self._find_column_index(headers, ['test', 'name', 'parameter'])
        value_col = self._find_column_index(headers, ['value', 'result', 'level'])
        unit_col = self._find_column_index(headers, ['unit', 'units', 'uom'])
        range_col = self._find_column_index(headers, ['range', 'reference', 'normal'])
        
        # Parse data rows
        for row in table[1:]:
            if len(row) <= max(test_col, value_col):
                continue
            
            test_name = row[test_col].strip() if test_col >= 0 else ''
            value_str = row[value_col].strip() if value_col >= 0 else ''
            
            if not test_name or not value_str:
                continue
            
            # Extract numeric value
            value = self._extract_numeric_value(value_str)
            
            lab_value = {
                'test_name': test_name,
                'value': value,
                'value_string': value_str,
                'unit': row[unit_col].strip() if unit_col >= 0 and unit_col < len(row) else '',
                'reference_range': row[range_col].strip() if range_col >= 0 and range_col < len(row) else ''
            }
            
            lab_values.append(lab_value)
        
        return lab_values
    
    def _parse_text_for_lab_values(self, text: str) -> List[Dict]:
        """
        Parse lab values from plain text
        
        Args:
            text: Extracted text
        
        Returns:
            List of lab test results
        """
        lab_values = []
        lines = text.split('\n')
        
        # Pattern: Test Name: Value Unit (Range)
        pattern = r'([A-Za-z\s]+):\s*([\d.]+)\s*([A-Za-z/%]+)?\s*(?:\(([\d.\-\s]+)\))?'
        
        for line in lines:
            matches = re.finditer(pattern, line)
            for match in matches:
                test_name = match.group(1).strip()
                value_str = match.group(2).strip()
                unit = match.group(3).strip() if match.group(3) else ''
                ref_range = match.group(4).strip() if match.group(4) else ''
                
                lab_value = {
                    'test_name': test_name,
                    'value': float(value_str) if value_str else None,
                    'value_string': value_str,
                    'unit': unit,
                    'reference_range': ref_range
                }
                
                lab_values.append(lab_value)
        
        return lab_values
    
    def compare_with_standards(self, lab_values: List[Dict]) -> List[Dict]:
        """
        Compare lab values with standard ranges
        
        Args:
            lab_values: List of lab test results
        
        Returns:
            Lab values with comparison results
        """
        db = get_mongodb()
        standards_collection = db['lab_test_standards']
        
        results = []
        
        for lab_value in lab_values:
            test_name = lab_value['test_name']
            value = lab_value.get('value')
            
            if value is None:
                results.append({
                    **lab_value,
                    'status': 'unknown',
                    'interpretation': 'Could not parse numeric value'
                })
                continue
            
            # Find standard in MongoDB
            standard = standards_collection.find_one(
                {'test_name': {'$regex': f'^{test_name}$', '$options': 'i'}}
            )
            
            if not standard:
                # Try partial match
                standard = standards_collection.find_one(
                    {'test_name': {'$regex': test_name, '$options': 'i'}}
                )
            
            if standard:
                # Compare with range
                normal_range = standard.get('normal_range', {})
                min_val = normal_range.get('min')
                max_val = normal_range.get('max')
                
                status = 'normal'
                interpretation = standard.get('interpretation', {}).get('normal', 'Within normal range')
                
                if min_val is not None and value < min_val:
                    status = 'low'
                    interpretation = standard.get('interpretation', {}).get('low', 'Below normal range')
                elif max_val is not None and value > max_val:
                    status = 'high'
                    interpretation = standard.get('interpretation', {}).get('high', 'Above normal range')
                
                # Check for critical values
                critical_range = standard.get('critical_range', {})
                if critical_range:
                    crit_min = critical_range.get('min')
                    crit_max = critical_range.get('max')
                    
                    if (crit_min is not None and value < crit_min) or \
                       (crit_max is not None and value > crit_max):
                        status = 'critical'
                        interpretation = 'Critical value - requires immediate attention'
                
                results.append({
                    **lab_value,
                    'status': status,
                    'interpretation': interpretation,
                    'normal_range': normal_range,
                    'critical_range': critical_range
                })
            else:
                results.append({
                    **lab_value,
                    'status': 'unknown',
                    'interpretation': 'No standard reference available'
                })
        
        return results
    
    def generate_analysis(self, lab_results: List[Dict]) -> Dict:
        """
        Generate patient-friendly analysis and recommendations
        
        Args:
            lab_results: Lab results with comparisons
        
        Returns:
            Analysis with interpretations and recommendations
        """
        # Categorize results
        normal_results = [r for r in lab_results if r.get('status') == 'normal']
        abnormal_results = [r for r in lab_results if r.get('status') in ['low', 'high']]
        critical_results = [r for r in lab_results if r.get('status') == 'critical']
        
        # Generate summary
        summary = self._generate_summary(normal_results, abnormal_results, critical_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(abnormal_results, critical_results)
        
        # Generate dietary suggestions
        dietary_suggestions = self._generate_dietary_suggestions(abnormal_results)
        
        # Medical disclaimer
        disclaimer = ("⚕️ **Important Medical Disclaimer**: This analysis is for informational purposes only "
                     "and does not constitute medical advice, diagnosis, or treatment. Lab results should always "
                     "be reviewed with your healthcare provider who can interpret them in the context of your "
                     "complete medical history and current health status.")
        
        return {
            'summary': summary,
            'normal_count': len(normal_results),
            'abnormal_count': len(abnormal_results),
            'critical_count': len(critical_results),
            'recommendations': recommendations,
            'dietary_suggestions': dietary_suggestions,
            'disclaimer': disclaimer
        }
    
    def _generate_summary(
        self,
        normal_results: List[Dict],
        abnormal_results: List[Dict],
        critical_results: List[Dict]
    ) -> str:
        """Generate summary text"""
        total = len(normal_results) + len(abnormal_results) + len(critical_results)
        
        if total == 0:
            return "No lab results to analyze."
        
        summary_parts = []
        
        if critical_results:
            summary_parts.append(
                f"🚨 **CRITICAL**: {len(critical_results)} test(s) show critical values requiring immediate medical attention."
            )
        
        if abnormal_results:
            summary_parts.append(
                f"⚠️ {len(abnormal_results)} test(s) are outside normal range."
            )
        
        if normal_results:
            summary_parts.append(
                f"✓ {len(normal_results)} test(s) are within normal range."
            )
        
        return ' '.join(summary_parts)
    
    def _generate_recommendations(
        self,
        abnormal_results: List[Dict],
        critical_results: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        if critical_results:
            recommendations.append(
                "🚨 Contact your healthcare provider immediately about critical values"
            )
            recommendations.append(
                "Do not wait for a scheduled appointment - this requires urgent attention"
            )
        
        if abnormal_results:
            recommendations.append(
                "📋 Schedule a follow-up appointment with your doctor to discuss abnormal results"
            )
            recommendations.append(
                "Bring this report to your appointment for detailed review"
            )
        
        recommendations.append(
            "📊 Keep track of your lab results over time to monitor trends"
        )
        recommendations.append(
            "💊 Continue taking prescribed medications unless advised otherwise by your doctor"
        )
        
        return recommendations
    
    def _generate_dietary_suggestions(self, abnormal_results: List[Dict]) -> List[str]:
        """Generate dietary suggestions based on abnormal results"""
        suggestions = []
        
        # Check for specific conditions
        test_names_lower = [r['test_name'].lower() for r in abnormal_results]
        
        if any('glucose' in name or 'sugar' in name for name in test_names_lower):
            suggestions.append("🍎 Monitor carbohydrate intake and choose complex carbs over simple sugars")
            suggestions.append("🥗 Include more fiber-rich foods in your diet")
        
        if any('cholesterol' in name or 'lipid' in name for name in test_names_lower):
            suggestions.append("🥑 Choose healthy fats (omega-3, monounsaturated) over saturated fats")
            suggestions.append("🐟 Include fatty fish like salmon in your diet")
            suggestions.append("🚫 Limit processed foods and trans fats")
        
        if any('iron' in name or 'hemoglobin' in name for name in test_names_lower):
            suggestions.append("🥩 Include iron-rich foods like lean meats, beans, and leafy greens")
            suggestions.append("🍊 Pair iron-rich foods with vitamin C for better absorption")
        
        if not suggestions:
            suggestions.append("🥗 Maintain a balanced diet with plenty of fruits and vegetables")
            suggestions.append("💧 Stay well hydrated")
        
        return suggestions
    
    def _find_column_index(self, headers: List[str], keywords: List[str]) -> int:
        """Find column index by keywords"""
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in keywords):
                return i
        return -1
    
    def _extract_numeric_value(self, value_str: str) -> Optional[float]:
        """Extract numeric value from string"""
        # Remove common non-numeric characters
        cleaned = re.sub(r'[<>≤≥]', '', value_str)
        
        # Extract first number
        match = re.search(r'[\d.]+', cleaned)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    def _get_content_type(self, file_name: str) -> str:
        """Get content type from file name"""
        ext = file_name.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    def _get_mock_extraction(self) -> Dict:
        """Get mock extraction data for development"""
        return {
            'text_lines': [
                'Lab Report',
                'Patient: John Doe',
                'Date: 2024-01-15',
                'Test Results:',
                'Glucose: 105 mg/dL (70-100)',
                'Cholesterol: 220 mg/dL (125-200)',
                'Hemoglobin: 14.5 g/dL (13.5-17.5)'
            ],
            'tables': [[
                ['Test Name', 'Value', 'Unit', 'Reference Range'],
                ['Glucose', '105', 'mg/dL', '70-100'],
                ['Cholesterol', '220', 'mg/dL', '125-200'],
                ['Hemoglobin', '14.5', 'g/dL', '13.5-17.5']
            ]],
            'full_text': 'Lab Report\nPatient: John Doe\nDate: 2024-01-15\nTest Results:\nGlucose: 105 mg/dL (70-100)\nCholesterol: 220 mg/dL (125-200)\nHemoglobin: 14.5 g/dL (13.5-17.5)'
        }
