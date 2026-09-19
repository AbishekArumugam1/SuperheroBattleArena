import asyncio
import pygame

pygame.init()

screen = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Pygbag Test")

font = pygame.font.Font(None, 70)

async def main():
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 20, 30))

        text = font.render("PYGBAG TEST WORKS!", True, (255, 255, 255))
        screen.blit(text, (220, 250))

        pygame.display.flip()

        await asyncio.sleep(0)

asyncio.run(main())
