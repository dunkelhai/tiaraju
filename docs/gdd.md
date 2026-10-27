# Tiaraju — Game Design Document (v0.1)

## Premissa

1756, Sete Povos das Missões. Sepé Tiaraju, corregedor de São Miguel Arcanjo, atravessa o
pampa e as ruínas do seu povo enquanto os exércitos luso-espanhóis avançam para cumprir o
Tratado de Madri. "Esta terra tem dono."

## Pilares

1. **Drama** — trilha orquestral-indígena, entardecer permanente, silêncio antes da batalha.
2. **Pixel art bonito** — 480x270, paleta de arenito e céu de fim de tarde, parallax profundo,
   luz de fogueira, glow.
3. **Controle preciso** — plataforma de ação com game feel caprichado; combate curto e direto
   com a lança.
4. **Memória** — cada ato é um lugar real (São Miguel, o pampa, Caiboaté) e um símbolo
   (a cruz missioneira, a lua/lunar de Sepé, a Terra sem Mal).

## Loop

Atravessar a fase da esquerda para a direita → enfrentar soldados → descansar nas cruzes
(checkpoint, cura) → chegar ao arco. Morrer devolve ao último ponto de descanso.

## Personagem

- **Sepé**: 3 corações. Corre (112 px/s), pula (~3,3 tiles), estoca com a lança (alcance ~24 px,
  3 frames, 0,27 s). Invulnerável 1,1 s após dano.
- Sprite 40x32, animações: idle, run (6), jump, fall, hurt, attack (3).

## Inimigos

- **Soldado** (2 de vida): patrulha e vira nas beiradas; ao ver Sepé a até 96 px, pausa 0,4 s
  (alerta) e dá um bote de baioneta (155 px/s por 0,36 s). Causa dano por toque e pela baioneta.
- Planejados: cavaleiro dragão (investida a cavalo), artilheiro (projétil em arco), capitão (mini-chefe).

## Atos

| Ato | Lugar | Clima | Chefe |
|-----|-------|-------|-------|
| I   | São Miguel Arcanjo (ruínas, pampa) | entardecer | capitão luso |
| II  | O pampa aberto, rio, Caiboaté | noite com lua, chuva | Gomes Freire / Andonaegui (batalha) |
| III | *Yvy Marã Ey* — a Terra sem Mal (onírico) | amanhecer dourado | a própria lenda |

## Trilha

- **Tema** *Esta terra tem dono* (ré menor, 90 BPM): intro (drone + flauta) → A (tambores)
  → B (cordas, coro) → C (metais, melodia em oitava, rulos) → outro, pensado para loop.
- **Lamento** (introdução): drone, flauta rubato, coro.
- Futuro: variação de batalha para o Ato II, tema de amanhecer para o Ato III, cantos guarani
  (vozes reais) se houver colaboração.

## Fora do escopo (por enquanto)

Loja, árvore de habilidades, inventário, diálogos ramificados.
