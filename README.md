# Abyssal – Dotfiles

## 🧰 **Inclui**
- 🎨 **Hyprland** → configuração com animações suaves e keybinds otimizados  
- 🧭 **Waybar** → barra superior com música, bateria, temperatura e workspaces  
- 🧠 **Rofi** → launcher estilizado em dark mode  
- 🖼 **Wallbash** → troca dinâmica de papéis de parede  
- 🧼 Dotfiles limpos e organizados para fácil manutenção

---

## 🛠 **Instalação**
> ⚠️ Testado em CachyOS + Hyprland 0.51.1  
> Recomendado para distribuições base Arch.

```bash
# Remova pacotes não utilizados (provindos do HyDE)
sudo pacman -Rns dunst

# Remova o Mako (caso utilizando CachyOS)
sudo pacman -Rdd mako

# Desative a inicialização do Mako nos arquivos do Hyprland
sudo nano ~/.config/hypr/config/autostart.conf

# Altere a linha a seguir e salve o arquivo
"exec-once = mako &" => "exec-once = swaync" 

# Instale pacotes necessários
sudo pacman -Syu swaync gvfs just

# Clone o repositório
git clone https://github.com/skalel/Abyssal.git ~/Abyssal-files

# Escolha os arquivos que deseja e copie os dotfiles
cp -r ~/Abyssal-files/* ~/<Destino>/

# Reinicie o Hyprland
hyprctl dispatch exec "hyprland reload"

```

🚀 Extra \
Recomendamos a instalação das fontes a seguir:
Inter, JetBrains Mono

📜 Licença \
Este projeto está licenciado sob a MIT License.
Sinta-se livre para adaptar, modificar e contribuir!

🙌 Créditos \ 
Base: HyDE

Wallpapers: pertencem aos respectivos autores / jogos

Tema criado por Kal-El

---

📎 TODO \
 Adicionar script de instalação automatizado