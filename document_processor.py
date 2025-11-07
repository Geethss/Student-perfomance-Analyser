"""
Document Processing Module
Handles conversion of uploaded images and PDFs to formats suitable for Gemini API
"""

import io
import base64
from PIL import Image
from pdf2image import convert_from_bytes
from pypdf import PdfReader
from typing import List, Tuple, Union
import streamlit as st


class DocumentProcessor:
    """Process images and PDFs for Gemini API consumption"""
    
    MAX_IMAGE_SIZE = (1024, 1024)  # Max dimensions for optimization
    
    @staticmethod
    def optimize_image(image: Image.Image) -> Image.Image:
        """
        Optimize image size while maintaining aspect ratio
        
        Args:
            image: PIL Image object
            
        Returns:
            Optimized PIL Image object
        """
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if image is too large
        if image.size[0] > DocumentProcessor.MAX_IMAGE_SIZE[0] or \
           image.size[1] > DocumentProcessor.MAX_IMAGE_SIZE[1]:
            image.thumbnail(DocumentProcessor.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def process_image_file(uploaded_file) -> List[Image.Image]:
        """
        Process an uploaded image file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of PIL Image objects
        """
        try:
            image = Image.open(uploaded_file)
            optimized_image = DocumentProcessor.optimize_image(image)
            return [optimized_image]
        except Exception as e:
            raise ValueError(f"Error processing image: {str(e)}")
    
    @staticmethod
    def process_pdf_file(uploaded_file) -> List[Image.Image]:
        """
        Process an uploaded PDF file and convert to images
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of PIL Image objects (one per page)
        """
        try:
            # Read PDF bytes
            pdf_bytes = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            # Convert PDF pages to images
            images = convert_from_bytes(
                pdf_bytes,
                dpi=200,  # Good quality for text recognition
                fmt='PNG'
            )
            
            # Optimize each image
            optimized_images = [DocumentProcessor.optimize_image(img) for img in images]
            
            return optimized_images
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}")
    
    @staticmethod
    def process_uploaded_file(uploaded_file) -> List[Image.Image]:
        """
        Process any uploaded file (image or PDF)
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of PIL Image objects
        """
        if uploaded_file is None:
            raise ValueError("No file uploaded")
        
        file_type = uploaded_file.type
        
        if file_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']:
            return DocumentProcessor.process_image_file(uploaded_file)
        elif file_type == 'application/pdf':
            return DocumentProcessor.process_pdf_file(uploaded_file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def image_to_bytes(image: Image.Image) -> bytes:
        """
        Convert PIL Image to bytes
        
        Args:
            image: PIL Image object
            
        Returns:
            Image bytes
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()
    
    @staticmethod
    def prepare_for_gemini(images: List[Image.Image]) -> List[dict]:
        """
        Prepare images in format expected by Gemini API
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            List of dictionaries with image data for Gemini
        """
        prepared_images = []
        for img in images:
            # Convert to bytes
            img_bytes = DocumentProcessor.image_to_bytes(img)
            prepared_images.append({
                'mime_type': 'image/png',
                'data': img_bytes
            })
        
        return prepared_images

