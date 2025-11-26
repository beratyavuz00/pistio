import flet as ft
import random
import time
import itertools

# --- KART YAPISI ---
SUITS = ["♠", "♣", "♥", "♦"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.color = "red" if suit in ["♥", "♦"] else "black"
        
        if rank.isdigit():
            self.value = int(rank)
        elif rank == "A":
            self.value = 1
        else:
            self.value = 0 

    def __str__(self):
        return f"{self.rank}{self.suit}"

def create_deck():
    deck = [Card(s, r) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck

# --- YENİ HESAPLAMA FONKSİYONU (OYUN SONU İÇİN) ---
def calculate_final_details(collected_cards, pisti_count):
    # Puanlar: A=1, J=1, ♣2=2, ♦10=3
    card_points = 0
    
    for card in collected_cards:
        if card.rank == "A": card_points += 1
        elif card.rank == "J": card_points += 1
        elif card.suit == "♣" and card.rank == "2": card_points += 2
        elif card.suit == "♦" and card.rank == "10": card_points += 3
    
    # Kart Çoğunluğu (27 ve üzeri)
    majority_points = 0
    if len(collected_cards) >= 27:
        majority_points = 10
        
    # Pişti Puanı
    pisti_points = pisti_count * 10
    
    total_score = card_points + majority_points + pisti_points
    
    return {
        "total": total_score,
        "card_p": card_points,
        "maj_p": majority_points,
        "pisti_p": pisti_points,
        "count": len(collected_cards)
    }

def main(page: ft.Page):
    page.title = "Açık Pişti"
    page.window.icon = "icon.png"
    page.window_width = 480
    page.window_height = 850
    page.bgcolor = "#1B5E20"
    page.vertical_alignment = "spaceBetween"

    # --- DEĞİŞKENLER ---
    deck = []
    player_hand = []
    cpu_hand = []
    board_cards = [] 
    
    # Listeler sadece kartları biriktirecek, puan hesaplamayacak
    player_collected = []
    cpu_collected = []
    
    # Pişti Sayaçları
    player_pisti_count = 0
    cpu_pisti_count = 0
    
    last_taker = None 
    game_log = []
    is_processing = False
    is_game_over = False 

    # --- UI ---
    cpu_row = ft.Row(alignment="center", spacing=-15)
    
    board_row = ft.Row(alignment="center", wrap=True, spacing=5)
    board_container = ft.Container(
        content=board_row,
        width=450, height=250,
        padding=10,
        border=ft.border.all(2, "white24"),
        border_radius=15,
        bgcolor="#2E7D32"
    )
    
    board_info = ft.Text("Masa Boş", color="white70", size=14)
    player_row = ft.Row(alignment="center", spacing=10)
    
    # YENİ SKOR TABLOSU (PUAN YOK, SAYAÇ VAR)
    stat_text_cpu = ft.Text("CPU: 0 Kart | 0 Pişti", color="white", weight="bold", size=14)
    stat_text_player = ft.Text("SEN: 0 Kart | 0 Pişti", color="white", weight="bold", size=14)
    
    score_board = ft.Container(
        content=ft.Row([stat_text_cpu, stat_text_player], alignment="spaceAround"),
        bgcolor="black54", padding=10, border_radius=10, margin=10
    )

    log_column = ft.Column(spacing=2)
    log_container = ft.Container(
        content=log_column,
        width=250, height=80,
        bgcolor="black45", border_radius=8, padding=8,
        alignment=ft.alignment.bottom_left
    )

    status_text = ft.Text("Oyun Başlıyor...", color="yellow", size=16, weight="bold", text_align="center")

    # --- GÖRÜNÜM ---
    def create_card_ui(card, is_clickable=False, on_click_fn=None):
        return ft.Container(
            content=ft.Column([
                ft.Text(card.rank, color=card.color, size=20, weight="bold"),
                ft.Text(card.suit, color=card.color, size=26),
            ], alignment="center", horizontal_alignment="center", spacing=0),
            width=65, height=100,
            bgcolor="white",
            border_radius=8,
            border=ft.border.all(1, "black"),
            on_click=lambda e: on_click_fn(card) if is_clickable and not is_game_over else None,
            animate=ft.Animation(300, "easeOut")
        )

    def create_back_card_ui():
        return ft.Container(
            width=55, height=85,
            bgcolor="#1565C0", border_radius=6, border=ft.border.all(2, "white"),
            content=ft.Icon("grid_3x3", color="white54"), margin=ft.margin.only(right=0)
        )

    def add_log(message, color="white70"):
        game_log.append({"msg": message, "color": color})
        if len(game_log) > 3: game_log.pop(0)
        log_column.controls.clear()
        for item in game_log:
            log_column.controls.append(ft.Text(item["msg"], size=12, color=item["color"]))
        page.update()

    # --- OYUN AKIŞI ---
    def start_game():
        nonlocal deck, player_hand, cpu_hand, board_cards, player_collected, cpu_collected, player_pisti_count, cpu_pisti_count, game_log, last_taker, is_processing, is_game_over
        deck = create_deck()
        player_collected = []
        cpu_collected = []
        player_pisti_count = 0
        cpu_pisti_count = 0
        last_taker = None 
        player_hand = []
        cpu_hand = []
        board_cards = []
        game_log = [] 
        log_column.controls.clear()
        is_processing = False
        is_game_over = False
        
        for _ in range(4): board_cards.append(deck.pop())
        
        add_log("Yeni Oyun Başladı", "yellow")
        deal_hands()
        update_ui()

    def deal_hands():
        nonlocal player_hand, cpu_hand
        if len(deck) == 0: return 

        for _ in range(4):
            if deck: player_hand.append(deck.pop())
            if deck: cpu_hand.append(deck.pop())
        
        status_text.value = f"EL DAĞITILDI (Deste: {len(deck)})"
        status_text.color = "yellow"
        update_ui()

    def check_capture(played_card, board):
        captured_cards = []
        is_pisti = False
        
        if played_card.rank == "J":
            captured_cards.extend(board)
            return captured_cards, False

        temp_board = board[:]
        match_found = False
        for card in reversed(temp_board):
            if card.rank == played_card.rank:
                captured_cards.append(card)
                temp_board.remove(card)
                match_found = True
                break

        if len(board) == 1 and match_found: is_pisti = True

        if not match_found and played_card.value > 0:
            target_sum = played_card.value
            numeric_board = [c for c in temp_board if c.value > 0]
            found_combo = []
            for r in range(1, len(numeric_board) + 1):
                for combo in itertools.combinations(numeric_board, r):
                    if sum(c.value for c in combo) == target_sum:
                        found_combo = list(combo)
                        break
                if found_combo: break
            if found_combo: captured_cards.extend(found_combo)
        
        return captured_cards, is_pisti

    def player_click_handler(card):
        nonlocal is_processing
        if is_processing or is_game_over: return
        is_processing = True
        play_card(card, "PLAYER")

    def play_card(card, who):
        nonlocal last_taker, player_pisti_count, cpu_pisti_count, is_processing
        
        if who == "PLAYER":
            idx = -1
            for i, c in enumerate(player_hand):
                if c.suit == card.suit and c.rank == card.rank:
                    idx = i; break
            if idx != -1: player_hand.pop(idx)
        else:
            if card in cpu_hand: cpu_hand.remove(card)

        captured_cards, is_pisti = check_capture(card, board_cards)
        
        if captured_cards:
            last_taker = who
            for c in captured_cards:
                try: board_cards.remove(c)
                except: pass
            
            # Sadece listeye ekle, puan hesaplama!
            total_captured = captured_cards + [card]
            
            names = ", ".join([c.rank for c in captured_cards])
            log_msg = f"{who}: {card.rank} ile [{names}] aldı."
            log_color = "cyan" if who == "PLAYER" else "red"
            
            if is_pisti:
                log_msg = f"{who} PİŞTİ YAPTI! ({card.rank})"
                log_color = "yellow"
                if who == "PLAYER": player_pisti_count += 1
                else: cpu_pisti_count += 1

            if who == "PLAYER":
                player_collected.extend(total_captured)
            else:
                cpu_collected.extend(total_captured)
                
            add_log(log_msg, log_color)
        else:
            board_cards.append(card)
            add_log(f"{who} attı: {card.rank}", "white70")

        update_ui()
        
        if who == "PLAYER":
            page.update()
            page.run_task(cpu_turn_delayed)
        else:
            if len(player_hand) == 0 and len(cpu_hand) == 0:
                if len(deck) == 0:
                    page.update()
                    time.sleep(0.5)
                    end_game()
                else:
                    time.sleep(0.5)
                    deal_hands()
                    is_processing = False 
            else:
                is_processing = False 

    async def cpu_turn_delayed(e=None):
        time.sleep(0.8)
        cpu_turn()

    def cpu_turn():
        if not cpu_hand: return
        best_card = None
        
        for c in cpu_hand:
            captured, is_p = check_capture(c, board_cards)
            if captured:
                best_card = c
                if is_p: break 
                if len(captured) >= 2: break
        
        if not best_card and len(board_cards) >= 2:
            for c in cpu_hand:
                if c.rank == "J": best_card = c; break
        
        if not best_card:
            safe = [c for c in cpu_hand if c.rank != "J" and c.rank != "A"]
            best_card = random.choice(safe) if safe else cpu_hand[0]

        play_card(best_card, "CPU")

    # --- OYUN SONU VE HESAPLAMA ---
    def end_game():
        nonlocal is_game_over
        is_game_over = True
        
        # 1. Yerde Kalanlar
        msg = ""
        if board_cards:
            card_names = ", ".join([c.rank for c in board_cards])
            if last_taker == "PLAYER":
                player_collected.extend(board_cards)
                msg = f"Yerdekiler ({card_names}) SANA yazıldı."
            elif last_taker == "CPU":
                cpu_collected.extend(board_cards)
                msg = f"Yerdekiler ({card_names}) CPU'ya yazıldı."
            board_cards.clear()
            update_ui()

        # 2. DETAYLI PUAN HESAPLAMA
        p_stats = calculate_final_details(player_collected, player_pisti_count)
        c_stats = calculate_final_details(cpu_collected, cpu_pisti_count)

        # Kazanan Belirle
        if p_stats["total"] > c_stats["total"]:
            res_title = "KAZANDIN! 🏆"
            res_color = "green"
        elif c_stats["total"] > p_stats["total"]:
            res_title = "KAYBETTİN! 💀"
            res_color = "red"
        else:
            res_title = "BERABERE 🤝"
            res_color = "orange"

        # --- DETAYLI SONUÇ TABLOSU (Dialog İçeriği) ---
        # Güzel bir tablo görünümü için string formatlama
        content = ft.Column([
            ft.Text(f"SEN: {p_stats['total']} PUAN", size=25, weight="bold", color="green"),
            ft.Text(f"CPU: {c_stats['total']} PUAN", size=25, weight="bold", color="red"),
            ft.Divider(),
            ft.Row([
                ft.Column([
                    ft.Text("SENİN DETAYLAR", weight="bold"),
                    ft.Text(f"Kart Puanı: {p_stats['card_p']}"),
                    ft.Text(f"Pişti ({player_pisti_count}): {p_stats['pisti_p']}"),
                    ft.Text(f"Kart Sayısı ({p_stats['count']}): +{p_stats['maj_p']}")
                ]),
                ft.VerticalDivider(),
                ft.Column([
                    ft.Text("CPU DETAYLAR", weight="bold"),
                    ft.Text(f"Kart Puanı: {c_stats['card_p']}"),
                    ft.Text(f"Pişti ({cpu_pisti_count}): {c_stats['pisti_p']}"),
                    ft.Text(f"Kart Sayısı ({c_stats['count']}): +{c_stats['maj_p']}")
                ]),
            ], alignment="spaceBetween"),
            ft.Container(height=10),
            ft.Text(msg, size=12, italic=True, color="grey")
        ], height=350, spacing=5)

        # Yedekli Buton (Masa Üstü)
        board_container.content = ft.Column([
            ft.Text("OYUN BİTTİ", size=30, weight="bold", color="white"),
            ft.Text(f"SEN: {p_stats['total']} - CPU: {c_stats['total']}", size=20, color="yellow"),
            ft.ElevatedButton("YENİ OYUN", on_click=lambda e: restart_wrapper(), bgcolor="green", color="white")
        ], alignment="center", horizontal_alignment="center")

        # Açılır Pencere
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(res_title, size=30, weight="bold", color=res_color, text_align="center"),
            content=content,
            actions=[ft.ElevatedButton("YENİ OYUN", on_click=lambda e: restart_wrapper(), bgcolor="green", color="white")],
            actions_alignment="center"
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def restart_wrapper():
        page.dialog.open = False
        board_container.content = board_row # Masayı eski haline getir
        start_game()

    def update_ui():
        if is_game_over: return

        cpu_row.controls.clear()
        for _ in cpu_hand: cpu_row.controls.append(create_back_card_ui())
            
        board_row.controls.clear()
        if board_cards:
            board_info.value = f"Masa: {len(board_cards)} Kart"
            for c in board_cards:
                board_row.controls.append(create_card_ui(c, is_clickable=False))
        else:
            board_info.value = "Masa Temizlendi"
            board_row.controls.append(ft.Text("TEMİZ", color="white24", size=30, weight="bold"))

        player_row.controls.clear()
        for card in player_hand:
            player_row.controls.append(create_card_ui(card, is_clickable=True, on_click_fn=player_click_handler))

        # ÜST BAR GÜNCELLEME (Sadece Sayaçlar)
        stat_text_cpu.value = f"CPU: {len(cpu_collected)} Kart | {cpu_pisti_count} Pişti"
        stat_text_player.value = f"SEN: {len(player_collected)} Kart | {player_pisti_count} Pişti"
        
        page.update()

    page.add(
        ft.Container(height=10),
        ft.Column([ft.Text("CPU", color="white54"), cpu_row], horizontal_alignment="center"),
        ft.Column([score_board, board_container, board_info, status_text], horizontal_alignment="center", spacing=10),
        
        ft.Column([
            ft.Row([log_container], alignment="start"), 
            ft.Column([player_row, ft.Text("Kartların", color="white54")], horizontal_alignment="center")
        ]),
        ft.Container(height=10)
    )

    start_game()

ft.app(target=main, assets_dir="assets")