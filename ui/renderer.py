import os
import random
from PySide6.QtGui import QPixmap, QPainter, QColor, QLinearGradient, QRadialGradient, QBrush, QPen, QFont
from PySide6.QtCore import Qt, QPoint, QRect

class EnvironmentRenderer:
    @staticmethod
    def draw_sky_ground(painter: QPainter, rect: QRect, state) -> None:
        time_of_day = getattr(state, "time_of_day", "Morning")
        
        # 1. Sky Gradient (Artist tones mapped to Kelvin temperatures)
        sky_grad = QLinearGradient(0, 0, 0, rect.height() * 0.45)
        if time_of_day == "Morning": # Morning Warm (~5500K)
            sky_grad.setColorAt(0.0, QColor("#F9F5EB")) 
            sky_grad.setColorAt(1.0, QColor("#A0C49D")) 
        elif time_of_day == "Evening": # Evening Golden (~3200K)
            sky_grad.setColorAt(0.0, QColor("#4A0E4E")) 
            sky_grad.setColorAt(0.6, QColor("#E25E3E")) 
            sky_grad.setColorAt(1.0, QColor("#F5F0BB")) 
        elif time_of_day == "Night": # Night Blue (~4800K)
            sky_grad.setColorAt(0.0, QColor("#080D1A")) 
            sky_grad.setColorAt(1.0, QColor("#1A2F4C")) 
        else: # Afternoon Bright (~6500K)
            sky_grad.setColorAt(0.0, QColor("#1D8AF4")) 
            sky_grad.setColorAt(1.0, QColor("#8BE8FC")) 
            
        painter.fillRect(QRect(0, 0, rect.width(), int(rect.height() * 0.45)), QBrush(sky_grad))
        
        # 2. Ground & Season Colors
        season = getattr(state, "season", "Spring")
        ground_rect = QRect(0, int(rect.height() * 0.45), rect.width(), int(rect.height() * 0.55))
        
        ground_grad = QLinearGradient(0, ground_rect.top(), 0, ground_rect.bottom())
        if season == "Spring":
            ground_grad.setColorAt(0.0, QColor("#86C8BC")) 
            ground_grad.setColorAt(1.0, QColor("#439A86"))
        elif season == "Summer":
            ground_grad.setColorAt(0.0, QColor("#A2FF86")) 
            ground_grad.setColorAt(1.0, QColor("#245953"))
        elif season == "Autumn":
            ground_grad.setColorAt(0.0, QColor("#F4D160")) 
            ground_grad.setColorAt(1.0, QColor("#8D5A38"))
        else: # Winter
            ground_grad.setColorAt(0.0, QColor("#EAF6F6")) 
            ground_grad.setColorAt(1.0, QColor("#B2C8DF"))
            
        painter.fillRect(ground_rect, QBrush(ground_grad))
        
        # 3. Ambient Background Mountain Polygons
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(40, 50, 90, 30))
        painter.drawPolygon([QPoint(120, 315), QPoint(270, 180), QPoint(420, 315)])
        painter.drawPolygon([QPoint(320, 315), QPoint(520, 140), QPoint(720, 315)])
        painter.drawPolygon([QPoint(620, 315), QPoint(800, 190), QPoint(980, 315)])

    @staticmethod
    def draw_background_walkers(painter: QPainter, rect: QRect, state) -> None:
        time_of_day = getattr(state, "time_of_day", "Morning")
        if time_of_day == "Night":
            return
            
        # Draw a little background traveler silhouette
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(80, 80, 80, 120))
        painter.drawEllipse(180, 300, 12, 24)
        painter.drawEllipse(182, 290, 8, 8)

class BuildingRenderer:
    @staticmethod
    def draw_base_silhouette(painter: QPainter, rect: QRect, state) -> None:
        r = state.restaurant
        lvl = r.level
        custom_name = r.name
        
        # Base settings
        painter.setPen(QPen(QColor("#1F1717"), 3))
        font = QFont("Georgia", 11, QFont.Bold)
        painter.setFont(font)
        
        if lvl == 0: # Street Vendor
            # Wood Cart Box
            painter.setBrush(QColor("#8D6240"))
            painter.drawRect(420, 310, 160, 90)
            # Spoke Wheels
            painter.setBrush(QColor("#3E2723"))
            painter.drawEllipse(440, 390, 30, 30)
            painter.drawEllipse(530, 390, 30, 30)
            # Text Banner
            painter.setBrush(QColor("#F5F5F5"))
            painter.drawRect(400, 260, 200, 35)
            painter.setPen(QColor("#3E2723"))
            painter.drawText(QRect(400, 260, 200, 35), Qt.AlignCenter, custom_name)
        elif lvl == 1: # Used Food Cart
            painter.setBrush(QColor("#7C5335"))
            painter.drawRect(400, 290, 200, 110)
            painter.setBrush(QColor("#F8F0E5"))
            painter.drawRect(390, 240, 220, 45) # Canopy
            painter.setPen(QColor("#3E2723"))
            painter.drawText(QRect(390, 240, 220, 45), Qt.AlignCenter, custom_name)
        elif lvl == 2: # Independent Food Cart
            painter.setBrush(QColor("#5C3D2E"))
            painter.drawRect(380, 270, 240, 130)
            painter.setBrush(QColor("#E25E3E"))
            painter.drawRect(370, 210, 260, 55) # Premium awning
            painter.setPen(QColor("white"))
            painter.drawText(QRect(370, 210, 260, 55), Qt.AlignCenter, custom_name)
        elif lvl == 3: # Edge Shop
            # Stone walls
            painter.setBrush(QColor("#9E9E9E"))
            painter.drawRect(350, 240, 300, 160)
            # Tiled Shingles Roof
            painter.setBrush(QColor("#A75D5D"))
            roof = [QPoint(330, 240), QPoint(500, 150), QPoint(670, 240)]
            painter.drawPolygon(roof)
            # Door & Window
            painter.setBrush(QColor("#5C3D2E"))
            painter.drawRect(380, 310, 50, 90) # Door
            painter.setBrush(QColor("#89C4E9"))
            painter.drawRect(520, 290, 80, 55) # Glass window
            painter.setPen(QColor("#1F1717"))
            painter.drawText(QRect(350, 160, 300, 35), Qt.AlignCenter, custom_name)
        else: # Town Restaurant
            # Brick Tavern Walls
            painter.setBrush(QColor("#8B3D3D"))
            painter.drawRect(300, 200, 400, 200)
            # Slate Roof
            painter.setBrush(QColor("#2B2E4A"))
            roof = [QPoint(270, 200), QPoint(500, 100), QPoint(730, 200)]
            painter.drawPolygon(roof)
            # Double Glass Arches
            painter.setBrush(QColor("#E4F9F5"))
            painter.drawRect(350, 240, 70, 90)
            painter.drawRect(580, 240, 70, 90)
            # Double wood doors
            painter.setBrush(QColor("#3A1F1F"))
            painter.drawRect(470, 300, 60, 100)
            painter.setPen(QColor("white"))
            painter.drawText(QRect(300, 110, 400, 40), Qt.AlignCenter, custom_name)

        # Draw structural upgrades
        if "outdoor_seating" in r.upgrades:
            # Draw outdoor tables in front of shop
            painter.setPen(QPen(QColor("#1F1717"), 2))
            painter.setBrush(QColor("#D7A86E"))
            painter.drawEllipse(340, 410, 45, 20)
            painter.drawEllipse(610, 410, 45, 20)

class CharacterRenderer:
    @staticmethod
    def draw_seated_npcs(painter: QPainter, rect: QRect, state) -> None:
        r = state.restaurant
        if r.level >= 3:
            # Barnaby sitting at window seat
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#1F4068")) # Dark blue coat
            painter.drawEllipse(535, 310, 20, 20)
            painter.setBrush(QColor("#FAD586")) # Face tint
            painter.drawEllipse(539, 300, 12, 12)
            painter.setBrush(QColor("#F0A500")) # Yellow hat
            painter.drawPolygon([QPoint(536, 300), QPoint(545, 290), QPoint(554, 300)])

class WeatherRenderer:
    @staticmethod
    def draw_weather_state(painter: QPainter, rect: QRect, state) -> None:
        climate = state.town.economic_climate
        random.seed(state.day * 15 + 4)
        
        if climate == "Monsoon Week":
            # Diagonal rain strokes
            painter.setPen(QPen(QColor(150, 210, 255, 100), 1))
            for _ in range(70):
                x = random.randint(0, rect.width())
                y = random.randint(0, rect.height())
                painter.drawLine(x, y, x - 10, y + 25)
        elif climate == "Economic Slowdown" or state.season == "Autumn":
            # Falling gold/orange leaves
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#C84B31"))
            for _ in range(12):
                x = random.randint(0, rect.width())
                y = random.randint(150, rect.height() - 100)
                painter.drawEllipse(x, y, 7, 4)

class LightingRenderer:
    @staticmethod
    def apply_sky_tint(painter: QPainter, rect: QRect, state) -> None:
        time_of_day = getattr(state, "time_of_day", "Morning")
        
        # Apply overlay tints to match light temperature
        if time_of_day == "Morning": # Morning Warm
            painter.fillRect(rect, QColor(255, 240, 160, 25))
        elif time_of_day == "Evening": # Evening Golden
            painter.fillRect(rect, QColor(230, 95, 30, 50))
        elif time_of_day == "Night": # Night Blue
            painter.fillRect(rect, QColor(10, 20, 50, 120))
            
            # Draw additive light spill from window if level >= 3 (Signature Effect)
            if state.restaurant.level >= 3:
                rad_grad = QRadialGradient(560, 310, 60)
                rad_grad.setColorAt(0.0, QColor(255, 220, 120, 150))
                rad_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(rad_grad))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(500, 250, 120, 120)

class EffectRenderer:
    @staticmethod
    def draw_steam_particles(painter: QPainter, rect: QRect, state) -> None:
        # Rising chimney steam
        r = state.restaurant
        if r.level >= 3:
            random.seed(state.day * 2)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 80))
            # Draw puff shapes above chimney area
            painter.drawEllipse(630 + random.randint(-5, 5), 120, 12, 8)
            painter.drawEllipse(625, 105, 16, 10)

class SceneComposer:
    @staticmethod
    def compose_restaurant(state, evening_phase: bool) -> QPixmap:
        pixmap = QPixmap(1000, 700)
        pixmap.fill(QColor("#EAD7BB")) # Sand background
        
        painter = QPainter(pixmap)
        rect = QRect(0, 0, 1000, 700)
        
        # Check if high-fidelity background image exists
        lvl = state.restaurant.level
        img_map = {
            0: "assets/images/shop_base_lvl0.jpg",
            1: "assets/images/shop_base_lvl1.jpg",
            2: "assets/images/shop_base_lvl2.jpg",
            3: "assets/images/autumn_evening_slice.jpg",
            4: "assets/images/shop_base_lvl4.jpg"
        }
        img_path = img_map.get(lvl, "assets/images/shop_base_lvl0.jpg")
        
        if os.path.exists(img_path):
            # Draw actual pixel art base background scene
            painter.drawPixmap(rect, QPixmap(img_path))
        else:
            # Fallback to fully procedural sky, ground, building vector drawing
            EnvironmentRenderer.draw_sky_ground(painter, rect, state)
            EnvironmentRenderer.draw_background_walkers(painter, rect, state)
            BuildingRenderer.draw_base_silhouette(painter, rect, state)
            CharacterRenderer.draw_seated_npcs(painter, rect, state)
            
        # Draw dynamic weather and particle effects on top
        WeatherRenderer.draw_weather_state(painter, rect, state)
        EffectRenderer.draw_steam_particles(painter, rect, state)
        
        # Override evening/night lighting phases dynamically
        if evening_phase:
            # Force evening golden tint
            painter.fillRect(rect, QColor(220, 90, 20, 60))
        else:
            LightingRenderer.apply_sky_tint(painter, rect, state)
            
        painter.end()
        return pixmap

    @staticmethod
    def compose_house(state) -> QPixmap:
        pixmap = QPixmap(1000, 700)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, 1000, 700)
        
        img_path = "assets/images/cottage_interior_slice.jpg"
        if os.path.exists(img_path):
            painter.drawPixmap(rect, QPixmap(img_path))
        else:
            # Fallback to procedural cottage walls & floor & furniture
            pixmap.fill(QColor("#5C3D2E")) # Deep warm wood floor
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#EAD7BB"))
            painter.drawRect(0, 0, 1000, 450)
            
            # Base wooden outlines
            painter.setPen(QPen(QColor("#3E2723"), 4))
            painter.drawLine(0, 450, 1000, 450)
            
            # Cottage furnishings from upgrades owned
            h = state.house
            partner = state.romance.partner
            
            # Fireplace
            if "fireplace" in h.upgrades:
                painter.setBrush(QColor("#757575"))
                painter.drawRect(450, 310, 100, 140)
                painter.setBrush(QColor("#1F1717"))
                painter.drawRect(470, 370, 60, 80)
                painter.setBrush(QColor("#E25E3E"))
                painter.drawEllipse(480, 390, 40, 40)
                
            # Dining Table
            if "dining_table" in h.upgrades:
                painter.setBrush(QColor("#3E2723"))
                painter.drawRect(680, 410, 140, 30) # Table top
                painter.drawRect(700, 440, 15, 60) # leg
                painter.drawRect(785, 440, 15, 60) # leg
                
                # Flower vase on table if quiet evening memory exists
                if partner and any(m.title == "Appreciated a Quiet Evening Together" for m in partner.memories):
                    painter.setBrush(QColor("#89C4E9"))
                    painter.drawRect(740, 380, 20, 30) # vase
                    painter.setBrush(QColor("#E25E3E"))
                    painter.drawEllipse(743, 370, 14, 14) # flowers
                    
            # Partner sitting reading if present
            if partner:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("#E25E3E") if partner.archetype == "Artist" else QColor("#1F4068"))
                painter.drawEllipse(840, 430, 25, 45) # body
                painter.setBrush(QColor("#FAD586"))
                painter.drawEllipse(845, 410, 15, 15) # head
            
        painter.end()
        return pixmap

    @staticmethod
    def compose_tavern(state) -> QPixmap:
        pixmap = QPixmap(1000, 700)
        painter = QPainter(pixmap)
        rect = QRect(0, 0, 1000, 700)
        
        img_path = "assets/images/tavern_interior_slice.jpg"
        if os.path.exists(img_path):
            painter.drawPixmap(rect, QPixmap(img_path))
        else:
            # Fallback to procedural tavern
            pixmap.fill(QColor("#3E2723"))
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#6A3825"))
            painter.drawRect(0, 0, 1000, 430)
            
            painter.setPen(QPen(QColor("#1F1717"), 3))
            painter.drawLine(0, 430, 1000, 430)
            
            # Warm hearth glow
            rad_grad = QRadialGradient(500, 200, 200)
            rad_grad.setColorAt(0.0, QColor(255, 200, 100, 130))
            rad_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(rad_grad))
            painter.drawEllipse(350, 50, 300, 300)
            
        painter.end()
        return pixmap
