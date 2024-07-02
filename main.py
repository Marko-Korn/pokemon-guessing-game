import csv
import requests
import random
import urllib.request
import io
import customtkinter
from PIL import ImageTk, Image as PILImage
from bs4 import BeautifulSoup
from tkinter import *

url = 'https://pokemondb.net/pokedex/national'

response = requests.get(url)

# Get every Pokémon, their types, and their image URL
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    pokemon_list = soup.find_all('div', class_='infocard')
    pokemon_data = []
    for pokemon in pokemon_list:
        name = pokemon.find('a', class_='ent-name').text
        types = [t.text for t in pokemon.find_all('a', class_='itype')]
        img_url = pokemon.find('img', class_='img-fixed img-sprite')['src']
        pokemon_data.append((name, types, img_url))

else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

# Insert all the pokemon data into a CSV
with open('pokemon_data.csv', 'w', newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Types', 'Image URL'])
    for name, types, img_url in pokemon_data:
        writer.writerow([name, ', '.join(types), img_url])

# Tkinter initialization
root = customtkinter.CTk()
root.geometry("1600x770")
root.title("Guess the Pokemon!")

image_label = None
random_pokemon = None
text_items = []


def get_random_pokemon():
    global random_pokemon, pokemon_image

    # Clear existing text items
    clear_text_items()

    display_name.delete(0, END)
    canvas.itemconfig(canvas_image, image=card_front_image)

    with open("pokemon_data.csv", "r") as f:
        reader = csv.reader(f)
        # Skip the header row
        next(reader)
        random_pokemon = random.choice(list(reader))
        display_image_from_url(random_pokemon[2])
        print(random_pokemon)


def display_image_from_url(link):
    global image_label, pokemon_image

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    req = urllib.request.Request(link, headers=headers)
    with urllib.request.urlopen(req) as u:
        raw_data = u.read()

    image = PILImage.open(io.BytesIO(raw_data))
    resized_image = image.resize((330, 212), PILImage.LANCZOS)  # Resize the image to 100x100
    photo = ImageTk.PhotoImage(resized_image)

    # If pokemon_image already exists, update it with the new image
    if pokemon_image:
        canvas.itemconfig(pokemon_image, image=photo)
    else:
        pokemon_image = canvas.create_image(36, 59, image=photo, anchor=NW)

    # Store reference to the image to avoid garbage collection
    canvas.image = photo


def check_input():
    global random_pokemon, text_items

    # Remove existing text items
    clear_text_items()

    if display_name.get().strip().lower() == random_pokemon[0].strip().lower():
        text_items.append(background_canvas.create_text(800, 190, text="You are correct!",
                                                        font=("Arial", 16, "bold"), fill="white"))
    else:
        text_items.append(background_canvas.create_text(800, 190, text="Wrong, try again!",
                                                        font=("Arial", 16, "bold"), fill="red"))


def clear_text_items():
    global text_items

    for item in text_items:
        background_canvas.delete(item)
    text_items = []


# Load the background image
background_image = PILImage.open("background.png")
background_image = background_image.resize((1600, 840), PILImage.LANCZOS)
background_photo = ImageTk.PhotoImage(background_image)

# Create a canvas to display the background image
background_canvas = Canvas(root, width=1600, height=840)
background_canvas.pack(fill="both", expand=True)
background_canvas.create_image(0, 0, image=background_photo, anchor="nw")

button = customtkinter.CTkButton(root, text="Random Pokemon!", command=get_random_pokemon, width=20, bg_color="#1f6aa5",
                                 font=("Arial", 16))
background_canvas.create_window(800, 30, anchor=CENTER, window=button)

display_name = Entry(root, width=25, font=("Arial", 12))
background_canvas.create_window(800, 109, anchor=CENTER, window=display_name)

display_name_label = background_canvas.create_text(800, 80, text="Guess the Pokemon:", font=("Arial", 16))

submit_button = customtkinter.CTkButton(root, text="Submit", command=check_input, width=20, bg_color="#1f6aa5",
                                        font=("Arial", 16))
background_canvas.create_window(800, 140, anchor=CENTER, window=submit_button)

# Convert the PIL Image to a PhotoImage
back_image = PILImage.open("back.png")
front_image = PILImage.open("front.png")
back_image = back_image.resize((400, 550), PILImage.LANCZOS)
front_image = front_image.resize((400, 550), PILImage.LANCZOS)
card_back_image = ImageTk.PhotoImage(back_image)
card_front_image = ImageTk.PhotoImage(front_image)

canvas = Canvas(root, height=550, width=400, background="#192653", highlightthickness=0)
background_canvas.create_window(800, 486, anchor=CENTER, window=canvas)
# Use the PhotoImage object in the create_image method
canvas_image = canvas.create_image(0, 0, image=card_back_image, anchor=NW)
pokemon_image = None  # Initialize pokemon_image as None

root.mainloop()
