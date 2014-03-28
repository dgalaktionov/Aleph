# -*- coding: utf-8 -*-

'''
Created on 15/03/2014

@author: DaGal
'''

import pygame
from Scene import Scene 
from Layer import Layer
from MessageScene import MessageScene
from EntityGroup import EntityGroup
from Camera import Camera
from Ui.HUD import HUD
import Constants
import MainMenu


class Level(Scene):

    def __init__(self, director, player):
        Scene.__init__(self, director)
        self.player = player
        self.enemyGroup = EntityGroup([])
        self.bulletGroup = EntityGroup([])
        self.groups = []
        self.groups.append(self.enemyGroup)
        self.groups.append(self.bulletGroup)

        self.bg = None
        self.collisionBg = None
        self.camera = Camera()

        self.HUD = HUD(self.director, (0, 467), True, player)
        hudLayer = Layer(self.director)
        hudLayer.append(self.HUD)
        self.layers.append(hudLayer)
        self.mouseHoveringHUD = False
        
        self.danger = False
        self.dangerLevel = 0
        
        self.gameOver = False

    def update(self, time):
        
        if self.gameOver:
            mainMenu = MainMenu.MainMenu(self.director)
            self.director.setScene(mainMenu)
            return
        
        if self.danger:
            self.dangerLevel = 210
            self.danger = False

        if self.collisionBg != None:
            self.player.update(time, self)
            for group in self.groups:
                group.update(time, self)

        self.camera.update(self.player)
        
        Scene.update(self, time)
        
        if self.gameOver:
            game_over_scene = MessageScene(self.director, self)
            game_over_scene.set_message("Has Muerto.")
            self.director.setScene(game_over_scene)

    def processEvent(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            m = MessageScene(self.director, self)
            self.director.setScene(m)

        self.player.controller.processEvent(event)
        Scene.processEvent(self, event)
        
    def drawDanger(self, screen):
        if self.dangerLevel > 0:    
            s = pygame.Surface((1000,750))  # the size of your rect
            s.set_alpha(self.dangerLevel)                # alpha level
            s.fill((255, 0, 0))           # this fills the entire surface
            screen.blit(s, (0,0))
            self.dangerLevel -= 10
            
    def drawRaytracing(self, screen):
        
        surf = self.director.screen

        collisionMap_mask = pygame.mask.from_surface(self.collisionBg)
        surf_mask = pygame.mask.from_surface(surf)
        overlap = collisionMap_mask.overlap_area(surf_mask, (0, 0))
        print overlap

        s = pygame.Surface((800,600), masks=collisionMap_mask)
        pygame.draw.rect(s, (255,0,0), (0,0,800,600))
        #s = pygame.Surface.convert(collisionMap_mask)

        self.director.screen.blit(self.collisionBg, (self.camera.state.x,self.camera.state.y))

        for bicho in self.enemyGroup:
            if bicho.controller.detect_player():
                pygame.draw.line(surf, (255,255,255), \
                (self.player.rect.x + self.camera.state.x, \
                 self.player.rect.y + self.camera.state.y), \
                (bicho.rect.x + self.camera.state.x, \
                 bicho.rect.y + self.camera.state.y))

    def draw(self, screen):
        screen.fill(0x000000)

        if self.bg:
            screen.blit(self.bg, self.camera.state)

        self.player.draw(screen, self.camera)
        for group in self.groups:
            group.draw(screen, self.camera)
        self.drawDanger(screen);
        if Constants.DEBUG:
            self.drawRaytracing(screen)
        # TODO: move maps and characters to its own layer
        Scene.draw(self, screen)  # draws rest of layers

    def game_over(self):
        """ Called when the player dies.
        """
        self.gameOver = True
