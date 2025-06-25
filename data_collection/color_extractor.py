#!/usr/bin/env python3
"""
Color Extraction Module for Fashion App

This module provides functionality to extract color information from clothing images,
including color palette, tone, hue, and shade analysis using Pylette (primary) and sklearn (fallback).
"""

import requests
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from io import BytesIO
import colorsys
from typing import List, Dict, Tuple, Optional
import os
from sklearn.cluster import KMeans
from tqdm import tqdm

# Try to import Pylette with fallback
try:
    from Pylette import extract_colors
    PYLETTE_AVAILABLE = True
except ImportError:
    tqdm.write("Warning: Pylette not available, will use sklearn only")
    PYLETTE_AVAILABLE = False
    extract_colors = None

# CSS color definitions with RGB values
CSS_COLORS = {
    "aliceblue": (240, 248, 255), "antiquewhite": (250, 235, 215), "aqua": (0, 255, 255), "aquamarine": (127, 255, 212), "azure": (240, 255, 255),
    "beige": (245, 245, 220), "bisque": (255, 228, 196), "black": (0, 0, 0), "blanchedalmond": (255, 235, 205), "blue": (0, 0, 255),
    "blueviolet": (138, 43, 226), "brown": (165, 42, 42), "burlywood": (222, 184, 135), "cadetblue": (95, 158, 160), "chartreuse": (127, 255, 0),
    "chocolate": (210, 105, 30), "coral": (255, 127, 80), "cornflowerblue": (100, 149, 237), "cornsilk": (255, 248, 220), "crimson": (220, 20, 60),
    "cyan": (0, 255, 255), "darkblue": (0, 0, 139), "darkcyan": (0, 139, 139), "darkgoldenrod": (184, 134, 11), "darkgray": (169, 169, 169),
    "darkgreen": (0, 100, 0), "darkgrey": (169, 169, 169), "darkkhaki": (189, 183, 107), "darkmagenta": (139, 0, 139), "darkolivegreen": (85, 107, 47),
    "darkorange": (255, 140, 0), "darkorchid": (153, 50, 204), "darkred": (139, 0, 0), "darksalmon": (233, 150, 122), "darkseagreen": (143, 188, 143),
    "darkslateblue": (72, 61, 139), "darkslategray": (47, 79, 79), "darkslategrey": (47, 79, 79), "darkturquoise": (0, 206, 209), "darkviolet": (148, 0, 211),
    "deeppink": (255, 20, 147), "deepskyblue": (0, 191, 255), "dimgray": (105, 105, 105), "dimgrey": (105, 105, 105), "dodgerblue": (30, 144, 255),
    "firebrick": (178, 34, 34), "floralwhite": (255, 250, 240), "forestgreen": (34, 139, 34), "fuchsia": (255, 0, 255), "gainsboro": (220, 220, 220),
    "ghostwhite": (248, 248, 255), "gold": (255, 215, 0), "goldenrod": (218, 165, 32), "gray": (128, 128, 128), "grey": (128, 128, 128),
    "green": (0, 128, 0), "greenyellow": (173, 255, 47), "honeydew": (240, 255, 240), "hotpink": (255, 105, 180), "indianred": (205, 92, 92),
    "indigo": (75, 0, 130), "ivory": (255, 255, 240), "khaki": (240, 230, 140), "lavender": (230, 230, 250), "lavenderblush": (255, 240, 245),
    "lawngreen": (124, 252, 0), "lemonchiffon": (255, 250, 205), "lightblue": (173, 216, 230), "lightcoral": (240, 128, 128), "lightcyan": (224, 255, 255),
    "lightgoldenrodyellow": (250, 250, 210), "lightgray": (211, 211, 211), "lightgreen": (144, 238, 144), "lightgrey": (211, 211, 211), "lightpink": (255, 182, 193),
    "lightsalmon": (255, 160, 122), "lightseagreen": (32, 178, 170), "lightskyblue": (135, 206, 250), "lightslategray": (119, 136, 153), "lightslategrey": (119, 136, 153),
    "lightsteelblue": (176, 196, 222), "lightyellow": (255, 255, 224), "lime": (0, 255, 0), "limegreen": (50, 205, 50), "linen": (250, 240, 230),
    "magenta": (255, 0, 255), "maroon": (128, 0, 0), "mediumaquamarine": (102, 205, 170), "mediumblue": (0, 0, 205), "mediumorchid": (186, 85, 211),
    "mediumpurple": (147, 112, 219), "mediumseagreen": (60, 179, 113), "mediumslateblue": (123, 104, 238), "mediumspringgreen": (0, 250, 154), "mediumturquoise": (72, 209, 204),
    "mediumvioletred": (199, 21, 133), "midnightblue": (25, 25, 112), "mintcream": (245, 255, 250), "mistyrose": (255, 228, 225), "moccasin": (255, 228, 181), "navajowhite": (255, 222, 173),
    "navy": (0, 0, 128), "oldlace": (253, 245, 230), "olive": (128, 128, 0), "olivedrab": (107, 142, 35), "orange": (255, 165, 0), "orangered": (255, 69, 0),
    "orchid": (218, 112, 214), "palegoldenrod": (238, 232, 170), "palegreen": (152, 251, 152), "paleturquoise": (175, 238, 238), "palevioletred": (219, 112, 147),
    "papayawhip": (255, 239, 213), "peachpuff": (255, 218, 185), "peru": (205, 133, 63), "pink": (255, 192, 203), "plum": (221, 160, 221), "powderblue": (176, 224, 230),
    "purple": (128, 0, 128), "rebeccapurple": (102, 51, 153), "red": (255, 0, 0), "rosybrown": (188, 143, 143), "royalblue": (65, 105, 225), "saddlebrown": (139, 69, 19),
    "salmon": (250, 128, 114), "sandybrown": (244, 164, 96), "seagreen": (46, 139, 87), "seashell": (255, 245, 238), "sienna": (160, 82, 45), "silver": (192, 192, 192),
    "skyblue": (135, 206, 235), "slateblue": (106, 90, 205), "slategray": (112, 128, 144), "slategrey": (112, 128, 144), "snow": (255, 250, 250), "springgreen": (0, 255, 127),
    "steelblue": (70, 130, 180), "tan": (210, 180, 140), "teal": (0, 128, 128), "thistle": (216, 191, 216), "tomato": (255, 99, 71), "turquoise": (64, 224, 208),
    "violet": (238, 130, 238), "wheat": (245, 222, 179), "white": (255, 255, 255), "whitesmoke": (245, 245, 245), "yellow": (255, 255, 0), "yellowgreen": (154, 205, 50)
}

class ColorExtractor:
    """Class for extracting and analyzing colors from images"""
    
    def __init__(self, palette_size: int = 5):
        """
        Initialize the color extractor
        
        Args:
            palette_size (int): Number of colors to extract from image
        """
        self.palette_size = palette_size
    
    def _find_closest_css_color(self, rgb: Tuple[int, int, int]) -> Tuple[str, float]:
        """
        Find the closest CSS color name for a given RGB color, using HSL hue for family detection.
        """
        import colorsys
        min_distance = float('inf')
        closest_color = "black"

        # Convert to HSL for hue-based family detection
        r, g, b = rgb
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        h_deg = h * 360

        # Determine color family by hue
        if l > 0.85:
            color_family = 'white'
        elif l < 0.15:
            color_family = 'black'
        elif s < 0.15:
            color_family = 'gray'
        elif h_deg < 15 or h_deg >= 345:
            color_family = 'red'
        elif h_deg < 45:
            color_family = 'orange'
        elif h_deg < 75:
            color_family = 'yellow'
        elif h_deg < 165:
            color_family = 'green'
        elif h_deg < 195:
            color_family = 'cyan'
        elif h_deg < 255:
            color_family = 'blue'
        elif h_deg < 285:
            color_family = 'purple'
        elif h_deg < 315:
            color_family = 'pink'
        else:
            color_family = 'red'

        # Family keywords for CSS color names
        family_keywords = {
            'red': ['red', 'crimson', 'maroon', 'firebrick', 'tomato', 'salmon', 'indianred'],
            'orange': ['orange', 'coral', 'chocolate', 'sienna', 'peru', 'tan', 'goldenrod'],
            'yellow': ['yellow', 'gold', 'khaki', 'beige', 'lemon', 'ivory'],
            'green': ['green', 'olive', 'lime', 'forest', 'seagreen', 'springgreen', 'lawngreen'],
            'cyan': ['cyan', 'aqua', 'turquoise', 'teal'],
            'blue': ['blue', 'navy', 'slateblue', 'royalblue', 'dodgerblue', 'skyblue', 'steelblue', 'midnightblue'],
            'purple': ['purple', 'violet', 'indigo', 'orchid', 'plum', 'rebeccapurple'],
            'pink': ['pink', 'hotpink', 'lightpink', 'deeppink', 'palevioletred'],
            'gray': ['gray', 'grey', 'slate', 'silver', 'gainsboro', 'whitesmoke', 'dimgray', 'darkgray', 'lightgray'],
            'white': ['white', 'snow', 'ivory', 'floralwhite', 'ghostwhite', 'seashell', 'linen', 'oldlace'],
            'black': ['black']
        }

        for css_name, css_rgb in CSS_COLORS.items():
            # Calculate Euclidean distance in RGB space
            distance = sum((a - b) ** 2 for a, b in zip(rgb, css_rgb)) ** 0.5
            css_name_lower = css_name.lower()

            # Apply strong bonus for matching color family
            if any(kw in css_name_lower for kw in family_keywords.get(color_family, [])):
                distance *= 0.5  # 50% bonus for matching family
            # Penalize gray/neutral names for colorful families
            if color_family not in ['gray', 'white', 'black'] and any(kw in css_name_lower for kw in family_keywords['gray']):
                distance *= 1.5  # 50% penalty for gray names on colorful tones
            # Penalize colorful names for gray/neutral families
            if color_family in ['gray', 'white', 'black'] and not any(kw in css_name_lower for kw in family_keywords[color_family]):
                distance *= 1.3  # 30% penalty for non-neutral names on neutral tones

            if distance < min_distance:
                min_distance = distance
                closest_color = css_name

        # Normalize distance to a 0-1 scale
        normalized_distance = min_distance / 441.67
        return closest_color, normalized_distance
    
    def download_image(self, image_url: str) -> Optional[Image.Image]:
        """
        Download image from URL
        
        Args:
            image_url (str): URL of the image to download
            
        Returns:
            PIL.Image.Image or None: Downloaded image or None if failed
        """
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return image
        except Exception as e:
            tqdm.write(f"Error downloading image from {image_url}: {str(e)}")
            return None
    
    def extract_colors_from_image(self, image: Image.Image) -> List[Dict]:
        """
        Extract color palette from image using Pylette (primary) and sklearn (fallback).
        Keeps all colors in palette but identifies background for dominant color selection.
        """
        # Always convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Try Pylette first if available
        if PYLETTE_AVAILABLE and extract_colors is not None:
            try:
                # Convert PIL image to numpy array for Pylette
                img_array = np.array(image)
                palette = extract_colors(img_array, palette_size=self.palette_size+1, resize=True)
                
                colors_data = []
                for color in palette:
                    try:
                        rgb = color.rgb
                        # Ensure RGB values are in correct range
                        rgb = tuple(max(0, min(255, int(c))) for c in rgb)
                        
                        # Convert to HSL and HSV
                        hsl = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                        hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                        
                        color_analysis = self._analyze_color(rgb, hsl, hsv)
                        
                        # Generate hex color manually since Pylette might not have hex attribute
                        hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
                        
                        # Find closest CSS color
                        css_color, css_distance = self._find_closest_css_color(rgb)
                        
                        color_data = {
                            'rgb': rgb,
                            'hex': hex_color,
                            'css_color': css_color,
                            'css_distance': css_distance,
                            'hsl': {
                                'hue': hsl[0] * 360,
                                'saturation': hsl[2] * 100,
                                'lightness': hsl[1] * 100
                            },
                            'hsv': {
                                'hue': hsv[0] * 360,
                                'saturation': hsv[1] * 100,
                                'value': hsv[2] * 100
                            },
                            'analysis': color_analysis,
                            'percentage': getattr(color, 'percentage', 0),  # Handle missing percentage
                            'is_background': self._is_background_color(getattr(color, 'percentage', 0), color_analysis)
                        }
                        colors_data.append(color_data)
                    except Exception as e:
                        tqdm.write(f"Error processing color from Pylette: {str(e)}")
                        continue
                
                # Return colors if Pylette worked
                if colors_data:
                    return colors_data[:self.palette_size]
                else:
                    raise Exception("Pylette returned no valid colors")
                    
            except Exception as e:
                tqdm.write(f"Error extracting colors with Pylette: {str(e)}")
                tqdm.write("Falling back to sklearn method...")
        
        # Fallback to sklearn
        return self._extract_colors_sklearn(image)

    def _extract_colors_sklearn(self, image: Image.Image) -> List[Dict]:
        """
        Fallback color extraction using sklearn KMeans clustering
        """
        try:
            # Resize image for faster processing
            image = image.resize((150, 150))
            img_array = np.array(image)
            
            # Ensure we have a 3-channel RGB image
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                pixels = img_array.reshape(-1, 3)
            else:
                # Convert to RGB if needed
                image = image.convert('RGB')
                img_array = np.array(image)
                pixels = img_array.reshape(-1, 3)
            
            # Use KMeans to cluster colors
            kmeans = KMeans(n_clusters=self.palette_size+1, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = kmeans.cluster_centers_.astype(int)
            labels = kmeans.labels_
            unique, counts = np.unique(labels, return_counts=True)
            total_pixels = len(pixels)
            
            colors_data = []
            for i, (color, count) in enumerate(zip(colors, counts)):
                try:
                    # Ensure RGB values are in correct range
                    rgb = tuple(max(0, min(255, int(c))) for c in color)
                    percentage = (count / total_pixels) * 100
                    
                    # Convert to HSL and HSV
                    hsl = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                    
                    color_analysis = self._analyze_color(rgb, hsl, hsv)
                    hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
                    
                    # Find closest CSS color
                    css_color, css_distance = self._find_closest_css_color(rgb)
                    
                    color_data = {
                        'rgb': rgb,
                        'hex': hex_color,
                        'css_color': css_color,
                        'css_distance': css_distance,
                        'hsl': {
                            'hue': hsl[0] * 360,
                            'saturation': hsl[2] * 100,
                            'lightness': hsl[1] * 100
                        },
                        'hsv': {
                            'hue': hsv[0] * 360,
                            'saturation': hsv[1] * 100,
                            'value': hsv[2] * 100
                        },
                        'analysis': color_analysis,
                        'percentage': percentage,
                        'is_background': self._is_background_color(percentage, color_analysis)
                    }
                    colors_data.append(color_data)
                except Exception as e:
                    tqdm.write(f"Error processing color from sklearn: {str(e)}")
                    # Create a fallback color entry
                    fallback_rgb = (128, 128, 128)
                    fallback_hsl = colorsys.rgb_to_hls(0.5, 0.5, 0.5)
                    fallback_hsv = colorsys.rgb_to_hsv(0.5, 0.5, 0.5)
                    fallback_analysis = self._analyze_color(fallback_rgb, fallback_hsl, fallback_hsv)
                    fallback_css_color, fallback_css_distance = self._find_closest_css_color(fallback_rgb)
                    
                    colors_data.append({
                        'rgb': fallback_rgb,
                        'hex': '#808080',
                        'css_color': fallback_css_color,
                        'css_distance': fallback_css_distance,
                        'hsl': {
                            'hue': fallback_hsl[0] * 360,
                            'saturation': fallback_hsl[2] * 100,
                            'lightness': fallback_hsl[1] * 100
                        },
                        'hsv': {
                            'hue': fallback_hsv[0] * 360,
                            'saturation': fallback_hsv[1] * 100,
                            'value': fallback_hsv[2] * 100
                        },
                        'analysis': fallback_analysis,
                        'percentage': 0,
                        'is_background': False
                    })
            
            return colors_data[:self.palette_size]
            
        except Exception as e:
            tqdm.write(f"Error in sklearn color extraction: {str(e)}")
            return []

    def _is_background_color(self, percentage: float, analysis: Dict) -> bool:
        """
        Determine if a color is likely a background color
        
        Args:
            percentage (float): Percentage of pixels this color represents
            analysis (Dict): Color analysis dictionary
            
        Returns:
            bool: True if likely background color
        """
        # More selective background detection - keep product colors
        
        # Very light colors (almost white) with any significant percentage
        if analysis.get('lightness', 0) > 0.9 and percentage > 5:
            return True
        
        # Pure white or very light gray with moderate percentage
        if analysis.get('tone') == 'white' and percentage > 15:
            return True
        
        # Very high percentage (>50%) regardless of tone
        if percentage > 50:
            return True
        
        # Light grayish colors with high percentage
        if (analysis.get('lightness', 0) > 0.7 and 
            analysis.get('saturation_value', 0) < 0.1 and 
            percentage > 30):
            return True
        
        return False

    def _remove_background_color(self, colors_data: List[Dict]) -> List[Dict]:
        """
        Remove background colors from the palette
        
        Args:
            colors_data (List[Dict]): List of color data dictionaries
            
        Returns:
            List[Dict]: Filtered color data without background colors
        """
        filtered_colors = []
        for color_data in colors_data:
            if not color_data.get('is_background', False):
                filtered_colors.append(color_data)
        
        # If we removed all colors, keep at least one
        if not filtered_colors and colors_data:
            filtered_colors = [colors_data[0]]
        
        return filtered_colors

    def extract_colors_from_url(self, image_url: str) -> List[Dict]:
        """
        Extract colors from image URL
        
        Args:
            image_url (str): URL of the image
            
        Returns:
            List[Dict]: List of color data dictionaries
        """
        image = self.download_image(image_url)
        if image is None:
            return []
        
        return self.extract_colors_from_image(image)

    def _analyze_color(self, rgb: Tuple[int, int, int], hsl: Tuple[float, float, float], hsv: Tuple[float, float, float]) -> Dict:
        """
        Analyze a color and determine its characteristics
        
        Args:
            rgb (Tuple[int, int, int]): RGB values
            hsl (Tuple[float, float, float]): HSL values (hue, lightness, saturation)
            hsv (Tuple[float, float, float]): HSV values (hue, saturation, value)
            
        Returns:
            Dict: Color analysis including tone, hue, shade, etc.
        """
        r, g, b = rgb
        h, l, s = hsl  # colorsys.rgb_to_hls returns (hue, lightness, saturation)
        h_hsv, s_hsv, v_hsv = hsv
        
        # Convert hue to degrees for comparison
        h_deg = h * 360
        
        # Determine tone (basic color family)
        if l < 0.15:
            tone = 'black'
        elif l > 0.85:
            tone = 'white'
        elif s < 0.15:
            tone = 'neutral'
        else:
            # Determine color tone based on hue (in degrees)
            if h_deg < 30 or h_deg >= 330:
                tone = 'red'
            elif h_deg < 60:
                tone = 'orange'
            elif h_deg < 90:
                tone = 'yellow'
            elif h_deg < 150:
                tone = 'green'
            elif h_deg < 210:
                tone = 'blue'
            elif h_deg < 270:
                tone = 'purple'
            elif h_deg < 330:
                tone = 'pink'
            else:
                tone = 'red'
        
        # Determine hue (specific color) - also using degrees
        if h_deg < 15 or h_deg >= 345:
            hue = 'red'
        elif h_deg < 45:
            hue = 'orange'
        elif h_deg < 75:
            hue = 'yellow'
        elif h_deg < 165:
            hue = 'green'
        elif h_deg < 255:
            hue = 'blue'
        elif h_deg < 285:
            hue = 'purple'
        elif h_deg < 315:
            hue = 'pink'
        else:
            hue = 'red'
        
        # Determine shade (lightness level)
        if l < 0.2:
            shade = 'dark'
        elif l < 0.4:
            shade = 'medium-dark'
        elif l < 0.6:
            shade = 'medium'
        elif l < 0.8:
            shade = 'medium-light'
        else:
            shade = 'light'
        
        # Determine saturation level
        if s < 0.2:
            saturation = 'muted'
        elif s < 0.5:
            saturation = 'soft'
        elif s < 0.8:
            saturation = 'vibrant'
        else:
            saturation = 'intense'
        
        # Determine if it's a warm or cool color (using degrees)
        if h_deg < 90 or h_deg >= 270:
            temperature = 'warm'
        else:
            temperature = 'cool'
        
        # Determine if it's a neutral color
        is_neutral = s < 0.15 or l < 0.15 or l > 0.85
        
        return {
            'tone': tone,
            'hue': hue,
            'shade': shade,
            'saturation': saturation,
            'temperature': temperature,
            'is_neutral': is_neutral,
            'lightness': l,
            'saturation_value': s
        }

    def create_color_visualization(self, colors_data: List[Dict], image_url: str = None, save_path: str = None) -> None:
        """
        Create a visualization of the extracted colors
        
        Args:
            colors_data (List[Dict]): List of color data dictionaries
            image_url (str, optional): Original image URL for reference
            save_path (str, optional): Path to save the visualization
        """
        if not colors_data:
            tqdm.write("No colors to visualize")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Color Analysis Visualization', fontsize=16, fontweight='bold')
        
        # 1. Color palette
        ax1 = axes[0, 0]
        ax1.set_title('Extracted Color Palette')
        
        for i, color_data in enumerate(colors_data):
            color = color_data['hex']
            percentage = color_data.get('percentage', 0)
            analysis = color_data['analysis']
            css_color = color_data.get('css_color', 'unknown')
            
            # Create color patch
            rect = patches.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=2)
            ax1.add_patch(rect)
            
            # Add text labels with CSS color name
            ax1.text(i + 0.5, 0.5, f"{percentage:.1f}%\n{analysis['tone']}\n{css_color}", 
                    ha='center', va='center', fontweight='bold', fontsize=9)
        
        ax1.set_xlim(0, len(colors_data))
        ax1.set_ylim(0, 1)
        ax1.set_xticks(range(len(colors_data)))
        ax1.set_xticklabels([f"Color {i+1}" for i in range(len(colors_data))])
        ax1.set_yticks([])
        
        # 2. Tone distribution
        ax2 = axes[0, 1]
        ax2.set_title('Tone Distribution')
        
        tone_counts = {}
        for color_data in colors_data:
            tone = color_data['analysis']['tone']
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
        
        if tone_counts:
            tones = list(tone_counts.keys())
            counts = list(tone_counts.values())
            # Use valid color names for matplotlib
            color_map = {
                'red': 'red', 'orange': 'orange', 'yellow': 'yellow', 'green': 'green',
                'blue': 'blue', 'purple': 'purple', 'pink': 'pink', 'neutral': 'gray',
                'white': 'white', 'black': 'black'
            }
            colors = [color_map.get(tone, 'gray') for tone in tones]
            bars = ax2.bar(tones, counts, color=colors)
            ax2.set_ylabel('Count')
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. CSS Color distribution
        ax3 = axes[1, 0]
        ax3.set_title('CSS Color Distribution')
        
        css_color_counts = {}
        for color_data in colors_data:
            css_color = color_data.get('css_color', 'unknown')
            css_color_counts[css_color] = css_color_counts.get(css_color, 0) + 1
        
        if css_color_counts:
            css_colors = list(css_color_counts.keys())
            counts = list(css_color_counts.values())
            bars = ax3.bar(css_colors, counts)
            ax3.set_ylabel('Count')
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. Shade distribution
        ax4 = axes[1, 1]
        ax4.set_title('Shade Distribution')
        
        shade_counts = {}
        for color_data in colors_data:
            shade = color_data['analysis']['shade']
            shade_counts[shade] = shade_counts.get(shade, 0) + 1
        
        if shade_counts:
            shades = list(shade_counts.keys())
            counts = list(shade_counts.values())
            bars = ax4.bar(shades, counts, color=['gray', 'darkgray', 'lightgray', 'silver', 'white'])
            ax4.set_ylabel('Count')
            ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            tqdm.write(f"Visualization saved to {save_path}")
        else:
            plt.show()
        
        plt.close()

    def get_dominant_colors_summary(self, colors_data: List[Dict]) -> Dict:
        """
        Get a summary of the dominant colors and overall characteristics
        
        Args:
            colors_data (List[Dict]): List of color data dictionaries
            
        Returns:
            Dict: Summary of color analysis
        """
        if not colors_data:
            return {
                'dominant_color': None,
                'overall_tone': 'unknown',
                'overall_hue': 'unknown',
                'overall_shade': 'unknown',
                'color_count': 0,
                'neutral_colors': 0,
                'warm_colors': 0,
                'cool_colors': 0
            }
        
        # Remove background colors for dominant color selection
        filtered_colors = self._remove_background_color(colors_data)
        
        if not filtered_colors:
            filtered_colors = colors_data  # Use all colors if no non-background colors
        
        # Find dominant color - prefer more saturated, non-neutral colors
        # Sort by: 1) non-neutral, 2) saturation (higher is better), 3) percentage
        def color_score(color_data):
            analysis = color_data['analysis']
            is_neutral = analysis.get('is_neutral', False)
            saturation = analysis.get('saturation_value', 0)
            percentage = color_data.get('percentage', 0)
            
            # Non-neutral colors get a huge boost
            neutral_penalty = 0 if not is_neutral else -1000
            
            # Saturation boost (0-1 scale)
            saturation_boost = saturation * 100
            
            # Percentage (but much less weight than saturation)
            percentage_boost = percentage * 0.1
            
            return neutral_penalty + saturation_boost + percentage_boost
        
        # Sort by score (highest first) and take the best
        sorted_colors = sorted(filtered_colors, key=color_score, reverse=True)
        dominant_color = sorted_colors[0] if sorted_colors else colors_data[0]
        
        # Count colors by characteristics
        tone_counts = {}
        hue_counts = {}
        shade_counts = {}
        css_color_counts = {}
        neutral_count = 0
        warm_count = 0
        cool_count = 0
        
        for color_data in colors_data:
            analysis = color_data['analysis']
            
            # Count tones
            tone = analysis['tone']
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
            
            # Count hues
            hue = analysis['hue']
            hue_counts[hue] = hue_counts.get(hue, 0) + 1
            
            # Count shades
            shade = analysis['shade']
            shade_counts[shade] = shade_counts.get(shade, 0) + 1
            
            # Count CSS colors
            css_color = color_data.get('css_color', 'unknown')
            css_color_counts[css_color] = css_color_counts.get(css_color, 0) + 1
            
            # Count temperature
            if analysis['temperature'] == 'warm':
                warm_count += 1
            else:
                cool_count += 1
            
            # Count neutrals
            if analysis['is_neutral']:
                neutral_count += 1
        
        # Determine overall characteristics
        overall_tone = max(tone_counts.items(), key=lambda x: x[1])[0] if tone_counts else 'unknown'
        overall_hue = max(hue_counts.items(), key=lambda x: x[1])[0] if hue_counts else 'unknown'
        overall_shade = max(shade_counts.items(), key=lambda x: x[1])[0] if shade_counts else 'unknown'
        overall_css_color = max(css_color_counts.items(), key=lambda x: x[1])[0] if css_color_counts else 'unknown'
        
        return {
            'dominant_color': {
                'rgb': dominant_color['rgb'],
                'hex': dominant_color['hex'],
                'css_color': dominant_color.get('css_color', 'unknown'),
                'tone': dominant_color['analysis']['tone'],
                'hue': dominant_color['analysis']['hue'],
                'shade': dominant_color['analysis']['shade'],
                'percentage': dominant_color.get('percentage', 0)
            },
            'overall_tone': overall_tone,
            'overall_hue': overall_hue,
            'overall_shade': overall_shade,
            'overall_css_color': overall_css_color,
            'color_count': len(colors_data),
            'neutral_colors': neutral_count,
            'warm_colors': warm_count,
            'cool_colors': cool_count,
            'tone_distribution': tone_counts,
            'hue_distribution': hue_counts,
            'shade_distribution': shade_counts,
            'css_color_distribution': css_color_counts
        }

def extract_colors_from_product_image(image_url: str, palette_size: int = 5) -> Dict:
    """
    Extract colors from a product image URL
    
    Args:
        image_url (str): URL of the product image
        palette_size (int): Number of colors to extract
        
    Returns:
        Dict: Dictionary containing color analysis results
    """
    try:
        extractor = ColorExtractor(palette_size=palette_size)
        colors_data = extractor.extract_colors_from_url(image_url)
        
        if not colors_data:
            return {
                'success': False,
                'error': 'No colors extracted',
                'colors': [],
                'summary': {
                    'dominant_color': None,
                    'overall_tone': 'unknown',
                    'overall_hue': 'unknown',
                    'overall_shade': 'unknown',
                    'color_count': 0,
                    'neutral_colors': 0
                }
            }
        
        # Get summary
        summary = extractor.get_dominant_colors_summary(colors_data)
        
        return {
            'success': True,
            'colors': colors_data,
            'summary': summary
        }
        
    except Exception as e:
        tqdm.write(f"Error extracting colors from {image_url}: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'colors': [],
            'summary': {
                'dominant_color': None,
                'overall_tone': 'unknown',
                'overall_hue': 'unknown',
                'overall_shade': 'unknown',
                'color_count': 0,
                'neutral_colors': 0
            }
        }

# Example usage
if __name__ == "__main__":
    # Test with a sample image URL
    test_url = "https://img01.ztat.net/article/spp-media-p1/1234567890/1234567890.jpg"
    
    tqdm.write("Testing color extraction...")
    result = extract_colors_from_product_image(test_url)
    
    if result['success']:
        tqdm.write("Color extraction successful!")
        tqdm.write(f"Found {len(result['colors'])} colors")
        tqdm.write(f"Dominant color: {result['summary']['dominant_color']['hex']}")
        tqdm.write(f"Overall tone: {result['summary']['overall_tone']}")
    else:
        tqdm.write(f"Color extraction failed: {result['error']}") 