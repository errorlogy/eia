# Neuraxon Game of Life  UI Renderer
# Based on the Paper "Neuraxon V2.0: A New Neural Growth & Computation Blueprint" by David Vivancos https://vivancos.com/  & Dr. Jose Sanchez  https://josesanchezgarcia.com/ for Qubic Science https://qubic.org/
# https://www.researchgate.net/publication/397331336_Neuraxon
# Play the Lite Version of the Game of Life at https://huggingface.co/spaces/DavidVivancos/NeuraxonLife
import pygame
import math
import numpy as np
from typing import Dict, List, Tuple, Optional

# Import constants and utilities
from config import T_SEA, T_LAND, T_ROCK
from utils import _clamp, _rot

# Type Checking import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulation.world import World
    from simulation.entities import NxEr, Food

class Renderer:
    """
    104O-2 TURBO Renderer — Headless leaderboard-only mode.

    Removes ALL visual map rendering (terrain, food sprites, NxEr sprites, effects).
    Keeps ONLY: leaderboard panel, stats, control buttons, detail panel, game-over modal.
    GUI refreshed once per second for maximum simulation throughput.
    """
    def __init__(self, world: 'World', textures: Dict[str, Optional[str]], textures_alpha: float, headless: bool = False):
        pygame.init()
        pygame.display.set_caption("Neuraxon Game of Life v4.0-TURBO (Headless)")
        self.screen = pygame.display.set_mode((480, 900), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.world = world
        self.headless = headless
        self.zoom = max(2.0, 800.0 / world.N)
        self.pan = [world.N * 0.5, world.N * 0.5]
        self.rot = 0.0
        self.dt = 1 / 60.0
        self.dragging = False
        self.drag_start = (0, 0)
        self.textures_alpha = 0
        self.font = pygame.font.SysFont("consolas", 16)
        self.small = pygame.font.SysFont("consolas", 14)
        self.big = pygame.font.SysFont("consolas", 20, bold=True)
        self.tex_land = None; self.tex_sea = None; self.tex_rock = None
        self.tex_food = None; self.tex_nxer = None
        self.button_rects = {}
        self.overlay_buttons = {}
        self.selected_nxer_id: Optional[int] = None
        self.detail_buttons: Dict[str, pygame.Rect] = {}
        self.ranking_click_areas: List[Tuple[pygame.Rect, str]] = []
        self.visual_mode = False

    def world_to_screen(self, x, y):
        return (0, 0)

    def screen_to_world(self, sx, sy) -> Tuple[float, float]:
        return (0.0, 0.0)

    def _draw_restart_modal(self):
        self.overlay_buttons = {}
        W, H = self.screen.get_size()
        bw, bh = 200, 48
        rect = pygame.Rect(W // 2 - 200, H // 2 - 100, 400, 200)
        pygame.draw.rect(self.screen, (15, 15, 18), rect, border_radius=12)
        pygame.draw.rect(self.screen, (90, 90, 100), rect, 2, border_radius=12)
        title = self.big.render("All NxErs have perished.", True, (235, 235, 240))
        subtitle = self.small.render("Auto-restart in 10s...", True, (220, 220, 220))
        self.screen.blit(title, (rect.x + (rect.w - title.get_width()) // 2, rect.y + 28))
        self.screen.blit(subtitle, (rect.x + (rect.w - subtitle.get_width()) // 2, rect.y + 60))
        y = rect.y + 110
        yes_rect = pygame.Rect(rect.x + 30, y, 150, bh)
        no_rect = pygame.Rect(rect.x + 220, y, 150, bh)
        for r, lab, key in [(yes_rect, "Yes", "restart_yes"), (no_rect, "No", "restart_no")]:
            pygame.draw.rect(self.screen, (35, 35, 45), r, border_radius=10)
            pygame.draw.rect(self.screen, (110, 110, 130), r, 2, border_radius=10)
            tx = self.big.render(lab, True, (235, 235, 240))
            self.screen.blit(tx, (r.x + (r.w - tx.get_width()) // 2, r.y + (bh - tx.get_height()) // 2))
            self.overlay_buttons[key] = r

    def draw_world(self, foods, nxers, hud, alive_count, dead_count, born_count, paused, effects, step_tick, GlobalTimeSteps, game_over, game_index, best_scores=None, ticks_per_sec=0):
        """104O-2 TURBO: Leaderboard-only. No map, no sprites, no effects."""
        self.screen.fill((10, 10, 14))
        w, h = self.screen.get_size()
        panel_w = min(460, w - 20)
        x = 10; y = 10

        round_text = self.big.render(f"TURBO  Round #{game_index}", True, (0, 255, 100))
        self.screen.blit(round_text, (x, y)); y += 24
        tps_text = self.small.render(f"Ticks/sec: {int(ticks_per_sec)}  |  Tick: {step_tick}", True, (180, 255, 180))
        self.screen.blit(tps_text, (x, y)); y += 22

        name2color = {a.name: a.color for a in nxers.values()}
        self.ranking_click_areas = []
        for title, rows in hud.items():
            display_title = title
            score = best_scores.get(title) if best_scores else None
            if score is not None: display_title = f"{title} ({score:.2f})" if isinstance(score, float) else f"{title} ({int(score)})"
            self.screen.blit(self.small.render(display_title, True, (180, 180, 180)), (x, y)); y += 18
            for name, val in rows[:3]:
                base_name = name.replace(" [Die]", "")
                base_name = base_name.split(" [", 1)[0].strip()
                dot_c = name2color.get(base_name, (200, 200, 200))
                pygame.draw.circle(self.screen, dot_c, (x + 8, y + 8), 5)
                name_text = self.small.render(f"{name}", True, (230, 230, 230))
                val_text = self.small.render(f"{val}", True, (220, 220, 220))
                name_rect = name_text.get_rect(topleft=(x + 20, y))
                val_rect = val_text.get_rect(topleft=(x + panel_w - 80, y))
                clicked_nxer_name = None
                for nxer_obj in nxers.values():
                    if nxer_obj.name == base_name: clicked_nxer_name = nxer_obj.name; break
                if clicked_nxer_name:
                    combined_rect = name_rect.union(val_rect)
                    self.ranking_click_areas.append((combined_rect, clicked_nxer_name))
                self.screen.blit(name_text, (x + 20, y))
                self.screen.blit(val_text, (x + panel_w - 80, y))
                y += 16
        y += 6

        self.screen.blit(self.small.render(f"Alive: {alive_count}", True, (220, 220, 220)), (x, y)); y += 18
        self.screen.blit(self.small.render(f"Dead : {dead_count}", True, (220, 220, 220)), (x, y)); y += 18
        self.screen.blit(self.small.render(f"Born : {born_count}", True, (220, 220, 220)), (x, y)); y += 24

        if nxers:
            alive_nxers = [a for a in nxers.values() if a.alive]
            if alive_nxers:
                sample = alive_nxers[:50] if len(alive_nxers) > 50 else alive_nxers
                avg_energy = np.mean([a.net.get_energy_status().get('average_energy', 0.0) for a in sample])
                avg_branching = np.mean([a.net.branching_ratio for a in sample])
                self.screen.blit(self.small.render(f"Avg Energy: {avg_energy:.1f} (sample)", True, (200, 200, 0)), (x, y)); y += 18
                self.screen.blit(self.small.render(f"Branching: {avg_branching:.2f}", True, (180, 180, 180)), (x, y)); y += 24

        self.button_rects = {}
        button_rows = [[("playpause", "Pause" if not paused else "Play"), ("exit", "Exit Game")], [("save", "Save Game"), ("load", "Load Game")], [("save_best", "Save Bests")]]
        bx, by_btn, bw_btn, bh_btn, pad = x, y, 120, 28, 8
        for row in button_rows:
            row_x = bx
            for key, lab in row:
                r = pygame.Rect(row_x, by_btn, bw_btn, bh_btn)
                pygame.draw.rect(self.screen, (35, 35, 40), r, border_radius=6)
                pygame.draw.rect(self.screen, (90, 90, 100), r, 1, border_radius=6)
                tx = self.small.render(lab, True, (230, 230, 230))
                self.screen.blit(tx, (r.x + (bw_btn - tx.get_width()) // 2, r.y + (bh_btn - tx.get_height()) // 2))
                self.button_rects[key] = r
                row_x += bw_btn + pad
            by_btn += bh_btn + pad

        self.detail_buttons = {}
        if paused and self.selected_nxer_id is not None and self.selected_nxer_id in nxers:
            a = nxers[self.selected_nxer_id]
            px, py_d = x, by_btn + 12
            pw = panel_w
            rect = pygame.Rect(px - 5, py_d - 5, pw + 10, 340)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), rect, border_radius=8)
            pygame.draw.rect(self.screen, (80, 80, 80), rect, 1, border_radius=8)
            gender_str = "Male" if a.is_male else "Female"
            title = f"{a.name} (id {a.id}) - {gender_str}"
            self.screen.blit(self.big.render(title, True, (230, 230, 230)), (px, py_d)); py_d += 28
            terrain_type = "Land" if a.can_land and not a.can_sea else ("Sea" if a.can_sea and not a.can_land else "Both")
            energy_status = a.net.get_energy_status() if hasattr(a.net, 'get_energy_status') else {}
            facts = [f"Color : {a.color}", f"Pos : {a.pos} Food : {a.food:.1f}", f"Alive : {a.alive} Terr: {terrain_type} Lived : {a.stats.time_lived_s:.1f}s", f"Found : {a.stats.food_found:.1f} Taken: {a.stats.food_taken:.1f}", f"Mates : {a.stats.mates_performed} Explr : {a.stats.explored}", f"Energy: {energy_status.get('average_energy', 0):.1f} Fitness: {a.stats.fitness_score:.3f}", f"Branching: {energy_status.get('branching_ratio', 0):.2f}"]
            for line in facts:
                self.screen.blit(self.small.render(line, True, (220, 220, 220)), (px, py_d)); py_d += 18
            py_d += 6
            self.screen.blit(self.small.render("Network params:", True, (200, 200, 200)), (px, py_d)); py_d += 18
            P = a.net.params
            main_params = [f"inputs={P.num_input_neurons} hidden={P.num_hidden_neurons} outputs={P.num_output_neurons}", f"conn_prob={P.connection_probability:.2f} steps={P.simulation_steps}", f"tau_fast={P.tau_fast:.2f} slow={P.tau_slow:.2f} meta={P.tau_meta:.2f}", f"thr_exc={P.firing_threshold_excitatory:.3f} thr_inh={P.firing_threshold_inhibitory:.3f}", f"learn={P.learning_rate:.3f} stdp_win={P.stdp_window:.3f}", f"dopamine={P.dopamine_baseline:.3f} serotonin={P.serotonin_baseline:.3f}", f"energy_cost={P.firing_energy_cost:.1f} meta_rate={P.metabolic_rate:.2f}", f"circles={len(a.net.itu_circles)} evolve_int={P.evolution_interval}"]
            for line in main_params:
                self.screen.blit(self.small.render(line, True, (210, 210, 210)), (px, py_d)); py_d += 16
            py_d += 10
            bw2, bh2, pad2 = 120, 26, 8
            detail_button_rows = [[("save_nxer", "Save NxEr"), ("load_nxer", "Load NxEr")], [("save_nxvizer", "Save NxVizer"), ("load_nxvizer", "Load NxVizer")]]
            for row in detail_button_rows:
                row_x = px
                for key, lab in row:
                    r = pygame.Rect(row_x, py_d, bw2, bh2)
                    pygame.draw.rect(self.screen, (35, 35, 40), r, border_radius=6)
                    pygame.draw.rect(self.screen, (90, 90, 100), r, 1, border_radius=6)
                    tx = self.small.render(lab, True, (230, 230, 230))
                    self.screen.blit(tx, (r.x + (bw2 - tx.get_width()) // 2, r.y + (bh2 - tx.get_height()) // 2))
                    self.detail_buttons[key] = r
                    row_x += bw2 + pad2
                py_d += bh2 + pad2

        if game_over: self._draw_restart_modal()
        pygame.display.flip()

    def handle_input(self, dt):
        pass

    def event_zoom_rotate_pan(self, ev):
        pass

    def button_clicked(self, pos) -> Optional[str]:
        for k, r in self.button_rects.items():
            if r.collidepoint(pos): return k
        for k, r in self.overlay_buttons.items():
            if r.collidepoint(pos): return k
        return None

    def detail_button_clicked(self, pos) -> Optional[str]:
        for k, r in self.detail_buttons.items():
            if r.collidepoint(pos): return k
        return None

    def ranking_clicked(self, pos) -> Optional[str]:
        for rect, name in self.ranking_click_areas:
            if rect.collidepoint(pos): return name
        return None

    def clear_detail(self):
        self.selected_nxer_id = None
        self.detail_buttons = {}

    def tick(self, fps_cap=60):
        self.dt = self.clock.tick(fps_cap) / 1000.0
        return self.dt