"""
Created on Tue Sep 1 14:05:12 2018

@author: Lucas Buk Cardoso RA: 15.03470-4
"""

import pygame
from pygame.locals import *
from random import randint
import os
from collections import deque
import time

Altura = 512
Largura = 512
white = (255,255,255)
black = (0,0,0)

class Canos():
    
    Largura = 80
    Altura = 32
    Tempo = 2000
    
    def __init__(self, topo_cano, corpo_cano):
        self.x = float(Largura - 1)
        self.vel = 0.18
        self.score = False
        self.img = pygame.Surface((Canos.Largura, Altura), SRCALPHA)
        self.img.convert()   
        self.img.fill((0,0,0,0))
        canos = int((Altura - 3 * Bird.Altura - 3 * Canos.Altura)/Canos.Altura)
        self.baixo = randint(1, canos)
        self.cima = canos - self.baixo

        # cano de baixo
        for i in range(1, self.baixo + 1):
            pos_cano = (0, Altura - i * Canos.Altura)
            self.img.blit(corpo_cano, pos_cano)
        topo_baixo_y = Altura - self.baixo * Canos.Altura
        final_baixo_cano = (0, topo_baixo_y - Canos.Altura)
        self.img.blit(topo_cano, final_baixo_cano)

        # cano de cima
        for i in range(self.cima):
            self.img.blit(corpo_cano, (0, i*Canos.Altura))
        topo_cima_y = self.cima * Canos.Altura
        self.img.blit(topo_cano, (0, topo_cima_y))

        # detectar colisão
        self.mask = pygame.mask.from_surface(self.img)

    @property
    def rect(self):
        return Rect(self.x, 0, Canos.Largura, Canos.Altura)

    def atualiza(self, delta_frames=1):
        self.x -= self.vel * (1000.0 * delta_frames/60)
        
    def coli(self, bird):
        return pygame.sprite.collide_mask(self, bird)        


class Bird():
    
    Largura = 32 
    Altura = 32 
    Tempo_subida = 333.3 

    def __init__(self, x, y, imagens):
        self.v = 0.0
        self.x = x 
        self.y = y  
        self.cima, self.baixo = imagens
        self.mask_cima = pygame.mask.from_surface(self.cima)
        self.mask_baixo = pygame.mask.from_surface(self.baixo)

    def atualiza(self):
        aceleracao = 0.125
        self.y -= self.v
        self.v -= aceleracao

    def img(self):
        if pygame.time.get_ticks() % 500 >= 200:
            return self.baixo
        else:
            return self.cima

    @property
    def mask(self):
        if pygame.time.get_ticks() % 500 >= 200:
            return self.mask_baixo
        else:
            return self.mask_cima
        
    @property
    def rect(self):
        return Rect(self.x, self.y, Bird.Largura, Bird.Altura)


class Jogo():

    pygame.init()
    pygame.mixer.music.load("Come Together.mp3")
    pygame.mixer.music.play()  
    
    def Play():
        tela = pygame.display.set_mode((Altura, Largura))
        pygame.display.set_caption('Flappy Bird')
        clock = pygame.time.Clock()
        fonte_score = pygame.font.SysFont(None, 45, bold=True)  
        imagens = Jogo.imagens()
        bird = Bird(50, int(Altura/2 - Bird.Altura/2), (imagens['bird2'], imagens['bird1']))
        canos = deque()
        frame_clock = 0  
        score = 0
        morreu = False
        inicio = False
        fim = False
        
        sorteio_fundo = randint(1,3)
        cor_cano = randint(1,4)
        if sorteio_fundo == 1:
            fundo = imagens['fundo_dia']
        elif sorteio_fundo == 2:
            fundo = imagens['fundo_noite']
        else: 
            fundo = imagens['fundo_pds']
                
        Telas.TelaInicio(bird, tela, fundo, inicio, sorteio_fundo)
        
        while not morreu:
            clock.tick(60)
            
            if not (frame_clock % (60 * Canos.Tempo/1000.0)):
                if cor_cano == 1:
                    p = Canos(imagens['topo_roxo'], imagens['corpo_roxo'])
                elif cor_cano == 2:
                    p = Canos(imagens['topo_verde'], imagens['corpo_verde'])
                elif cor_cano == 3: 
                    p = Canos(imagens['topo_verdeagua'], imagens['corpo_verdeagua'])
                else:
                    p = Canos(imagens['topo_vermelho'], imagens['corpo_vermelho'])
                canos.append(p)
                
            for tecla in pygame.event.get():
                if (tecla.type == KEYUP and tecla.key == K_SPACE):
                    bird.v = 4.0
                elif tecla.type == QUIT or (tecla.type == KEYUP and tecla.key == K_ESCAPE):
                    pygame.mixer.music.stop()
                    pygame.quit()
    
            # checagem de colisões
            colisao_cano = any(c.coli(bird) for c in canos)
            if colisao_cano or 0 >= bird.y or bird.y >= Altura - Bird.Altura:
                morreu = True
    
            tela.blit(fundo, (0, 0))
    
            while canos and not (-Canos.Largura < canos[0].x < Largura):
                canos.popleft()
    
            for c in canos:
                c.atualiza()
                tela.blit(c.img, c.rect)
            
            bird.atualiza()
            tela.blit(bird.img(), bird.rect)
    
            #Contagem do score
            for c in canos:
                if c.x + Canos.Largura < bird.x and not c.score:
                    score += 1
                    c.score = True
            tela_score = fonte_score.render(str(score), True, white)
            score_x = Largura/2 - tela_score.get_width()/2
            tela.blit(tela_score, (score_x, Canos.Altura))
            
            pygame.display.flip()
            frame_clock += 1
        
        Telas.TelaGameOver(tela, fundo, sorteio_fundo)    
        Telas.TelaFim(tela, fundo, score, fim, sorteio_fundo)
        
    def imagens():
        return {'bird2': Jogo.carrega('bird2.png'),'bird1': Jogo.carrega('bird1.png'),'fundo_dia': Jogo.carrega('FundoDia.png'),
                'fundo_noite': Jogo.carrega('FundoNoite.png'),'fundo_pds': Jogo.carrega('FundoPorDoSol.png'),
                'topo_roxo': Jogo.carrega('Corpo2Roxo.png'),'corpo_roxo': Jogo.carrega('CorpoRoxo.png'),
                'topo_verde': Jogo.carrega('Corpo2Verde.png'),'corpo_verde': Jogo.carrega('CorpoVerde.png'),
                'topo_verdeagua': Jogo.carrega('Corpo2VerdeAgua.png'),'corpo_verdeagua': Jogo.carrega('CorpoVerdeAgua.png'),
                'topo_vermelho': Jogo.carrega('Corpo2Vermelho.png'),'corpo_vermelho': Jogo.carrega('CorpoVermelho.png')}
        
    def carrega(img_nome):
        img = pygame.image.load(os.path.join('.', 'imagens', img_nome))
        return img
    
    def MaiorPont(score):
        arquivo = open('Recorde.txt','r')
        b = arquivo.readlines()
        anterior = int(b[0])
        if int(score) > anterior:
            arquivo.close()
            novo = open('Recorde.txt','w')
            novo.write(str(score))
            novo.close()
            return score
        return anterior


class Telas():
    
    def TelaInicio(bird, tela, fundo, inicio, sorteio_fundo):
        while not inicio:
            tela.blit(fundo, (0, 0))
            tela.blit(bird.img(), (Largura/2 - 25, Altura/2 - 20))
            nome_fonte = pygame.font.SysFont(None, 80, bold=True)
            tela_nome = nome_fonte.render('Flappy Bird', True, white)
            nome_x = Largura/2 - 180
            nome_y = Altura/2 - 130
                        
            instru_fonte = pygame.font.SysFont(None, 24, bold=True)
            if sorteio_fundo == 2:
                instru = instru_fonte.render('APERTE ESPAÇO PARA INICIAR', True, white)
            else:
                instru = instru_fonte.render('APERTE ESPAÇO PARA INICIAR', True, black)
            instru_x = Largura/2 - 140
            instru_y = Altura/2 + 170
                        
            tela.blit(tela_nome, (nome_x, nome_y))
            tela.blit(instru, (instru_x, instru_y))
            pygame.display.flip()
            for tecla in pygame.event.get():
                if (tecla.type == KEYUP and tecla.key == K_SPACE):
                    inicio = True
                elif tecla.type == QUIT or (tecla.type == KEYUP and tecla.key == K_ESCAPE):
                    pygame.mixer.music.stop()
                    pygame.quit()
        
    def TelaFim(tela, fundo, score, fim, sorteio_fundo):
        while not fim:
            tela.blit(fundo, (0, 0))
            fonte_score = pygame.font.SysFont(None, 70, bold=True)
            fonte_recorde = pygame.font.SysFont(None, 40, bold=True)
            best = Jogo.MaiorPont(score)

            tela_score = fonte_score.render('Score: ' + str(score), True, white)
            tela_recorde = fonte_recorde.render('Maior Pontuação: ' + str(best), True, white)
            score_x = Largura/2 - 120
            score_y = Altura/2 - 120
            tela.blit(tela_score, (score_x, score_y))
            
            recorde_x = Largura/2 - 160
            recorde_y = Altura/2 - 60
            tela.blit(tela_recorde, (recorde_x, recorde_y))
                
            instru_fonte = pygame.font.SysFont(None, 24, bold=True)
            if sorteio_fundo == 2:
                instru = instru_fonte.render('APERTE ESPAÇO PARA REINICIAR', True, white)
            else: 
                instru = instru_fonte.render('APERTE ESPAÇO PARA REINICIAR', True, black)
            instru_x = Largura/2 - 160
            instru_y = Altura/2 + 190
            tela.blit(instru, (instru_x, instru_y))
                
            pygame.display.flip()
            for tecla in pygame.event.get():
                if (tecla.type == KEYUP and tecla.key == K_SPACE):
                    Jogo.Play()
                elif tecla.type == QUIT or (tecla.type == KEYUP and tecla.key == K_ESCAPE):
                    fim = True
                
        pygame.mixer.music.stop()
        pygame.quit()   
        
    def TelaGameOver(tela, fundo, sorteio_fundo):
        tela.blit(fundo, (0, 0))
        gameover_fonte = pygame.font.SysFont(None, 60, bold=True)
        if sorteio_fundo == 2:
            gameover = gameover_fonte.render('GAME OVER!', True, white)
        else:
            gameover = gameover_fonte.render('GAME OVER!', True, black)
        gameover_x = Largura/2 - 160
        gameover_y = Altura/2 - 120
        tela.blit(gameover, (gameover_x, gameover_y))
        pygame.display.flip()
        time.sleep(1.5)
 
Jogo.Play()

