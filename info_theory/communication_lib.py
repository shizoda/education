import heapq
from collections import Counter
import pandas as pd
import graphviz
from IPython.display import Image, display
import json
import os

def format_binary_string(binary_string, chunk_size=7, max_length=50):
    if len(binary_string) > max_length:
        binary_string = binary_string[:max_length] + "..."
    formatted_string = ' '.join([binary_string[i:i+chunk_size] for i in range(0, len(binary_string), chunk_size)])
    return formatted_string


class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    freq = Counter(text)
    heap = [HuffmanNode(char, freq) for char, freq in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)
        merged = HuffmanNode(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2
        heapq.heappush(heap, merged)

    return heap[0], freq

def build_codes(node, prefix="", codebook={}):
    if node is not None:
        if node.char is not None:
            codebook[node.char] = prefix
        build_codes(node.left, prefix + "0", codebook)
        build_codes(node.right, prefix + "1", codebook)
    return codebook

def plot_huffman_tree(node):
    dot = graphviz.Digraph()

    def add_nodes_edges(node, parent=None, edge_label=""):
        if node:
            if node.char:
                label = f"{node.char} ({node.freq})"
                color = "lightpink"
            else:
                label = str(node.freq)
                color = "lightblue"

            dot.node(str(id(node)), label=label, style="filled", fillcolor=color)

            if parent:
                dot.edge(str(id(parent)), str(id(node)), label=edge_label)
            add_nodes_edges(node.left, node, "0")
            add_nodes_edges(node.right, node, "1")

    add_nodes_edges(node)
    return dot

def huffman_encoding(text):
    root, freq_table = build_huffman_tree(text)

    # Create and display frequency table
    freq_df = pd.DataFrame(freq_table.items(), columns=['Character', 'Frequency']).T
    display(freq_df)

    codebook = build_codes(root)

    # Create and display codebook table
    codebook_df = pd.DataFrame(codebook.items(), columns=['Character', 'Code'])
    display(codebook_df)

    encoded_text = ''.join(codebook[char] for char in text)
    encoded_text_breaks = ' '.join(codebook[char] for char in text)

    if len(encoded_text_breaks) >= 80:
        encoded_text_breaks = encoded_text_breaks[:80] + "..."

    print("\nHuffman Encoded: " + encoded_text_breaks)

    padding_length = (4 - len(encoded_text) % 4) % 4
    encoded_text += '0' * padding_length

    display_huffman_tree(plot_huffman_tree(root))

    return encoded_text, codebook, padding_length #, root

def huffman_decoding(encoded_text, codebook, padding_length):
    reverse_codebook = {v: k for k, v in codebook.items()}
    
    if padding_length > 0:
        encoded_text = encoded_text[:-padding_length]  # パディングを除去
    
    decoded_text = []
    decoded_data = []
    current_code = ""
    
    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_data.append(str(current_code))
            decoded_text.append(reverse_codebook[current_code])
            current_code = ""
    decoded_data_str = ' '.join(decoded_data)
    if len(decoded_data_str) >= 80:
        decoded_data_str = decoded_data_str[:80] + "..."
    
    print()
    print("Codebook: ",  ' '.join(f"{c}:{codebook[c]}" for c in sorted(codebook.keys(), key=lambda x: len(codebook[x]))))
    
    print()
    print(f"Huffman decoded: {decoded_data_str}")
    
    decoded_text = ''.join(decoded_text)
    return decoded_text

def display_huffman_tree(dot):
    dot.render('huffman_tree', format='png', cleanup=True)
    display(HTML(f"""
    <div style="display:flex; justify-content:center;">
        <img src="huffman_tree.png" style="height:400px;">
    </div>
    """))

color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}

def print_color(text, color="red"):
    return color_dic[color] + text + color_dic["end"]

def format_binary_string(binary_string, chunk_size=7, max_length=50):
    if len(binary_string) > max_length:
        binary_string = binary_string[:max_length] + "..."
    formatted_string = ' '.join([binary_string[i:i+chunk_size] for i in range(0, len(binary_string), chunk_size)])
    return formatted_string

def hamming_encode(data):
    print(f"Hamming Input  : {format_binary_string(data, 4)}")

    def calculate_parity_bits(bits):
        p1 = bits[0] ^ bits[1] ^ bits[3]
        p2 = bits[0] ^ bits[2] ^ bits[3]
        p3 = bits[1] ^ bits[2] ^ bits[3]
        return [p1, p2, p3]

    encoded_data = []
    for i in range(0, len(data), 4):
        block = [int(bit) for bit in data[i:i+4]]
        if len(block) < 4:
            block.extend([0] * (4 - len(block)))  # Padding with zeros if less than 4 bits
        parity_bits = calculate_parity_bits(block)
        encoded_block = [parity_bits[0], parity_bits[1], block[0], parity_bits[2], block[1], block[2], block[3]]
        encoded_data.extend(encoded_block)

    encoded_str = ''.join(map(str, encoded_data))
    formatted_encoded_str = format_binary_string(encoded_str, 7)
    formatted_encoded_str = ''.join([print_color(bit, 'blue') if i % 8 in [0, 1, 3] else bit for i, bit in enumerate(formatted_encoded_str)])#.replace(" ", ""))])

    print(f"Hamming Encoded: {formatted_encoded_str}")
    return encoded_str

def hamming_decode(data):
    def calculate_error_syndrome(bits):
        p1 = bits[0] ^ bits[2] ^ bits[4] ^ bits[6]
        p2 = bits[1] ^ bits[2] ^ bits[5] ^ bits[6]
        p3 = bits[3] ^ bits[4] ^ bits[5] ^ bits[6]
        return p1, p2, p3

    decoded_data = []
    decoded_data_all = []
    n_corrected = 0
    corrected_blocks = []

    for i in range(0, len(data), 7):
        block = [int(bit) for bit in data[i:i+7]]
        p1, p2, p3 = calculate_error_syndrome(block)
        error_position = p1 + (p2 << 1) + (p3 << 2)
        original_block = ''.join(map(str, block))
        if error_position:
            block[error_position - 1] ^= 1  # Correct the error
            corrected = ''.join(map(str, block))
            if n_corrected < 10:
                corrected_blocks.append((i, error_position, original_block, corrected))
            n_corrected += 1

        decoded_block = [block[2], block[4], block[5], block[6]]
        decoded_data.extend(decoded_block)
        decoded_data_all.extend(block)

    decoded_str = ''.join(map(str, decoded_data))
    decoded_str_all = ''.join(map(str, decoded_data_all))

    # Print the corrected blocks
    print(f"{n_corrected} corrections in total.")
    for i, error_position, original, corrected in corrected_blocks:
        print(f"  (Block-{i//7}, Bit-{error_position-1}): {format_binary_string(original)} --> {format_binary_string(corrected)}")
    if n_corrected > 10:
        print("      etc.")

    formatted_data = format_binary_string(data, 7)
    formatted_data = ''.join([print_color(bit, 'blue') if i % 8 in [0, 1, 3] else bit for i, bit in enumerate(formatted_data)])
    formatted_decoded_str_all = format_binary_string(decoded_str_all, 7)
    formatted_decoded_str_all = ''.join([print_color(bit, 'blue') if i % 7 in [0, 1, 3] else bit for i, bit in enumerate(formatted_decoded_str_all.replace(" ", ""))])
    formatted_decoded_str = format_binary_string(decoded_str, 4)

    print("Received       :", formatted_data)
    print("Hamming Decoded:", formatted_decoded_str_all)
    print("Hamming Output :", formatted_decoded_str)
    return decoded_str


import random

def introduce_errors(encoded_data, error_rate):
    result = []
    flip_prohibited_count = 0  # 反転禁止カウンター
    error_indices = []

    for i, bit in enumerate(encoded_data):
        if flip_prohibited_count > 0:
            result.append(bit)
            flip_prohibited_count -= 1
        else:
            if random.random() < error_rate:
                flipped_bit = '1' if bit == '0' else '0'
                result.append(flipped_bit)
                error_indices.append(i)
                flip_prohibited_count = 6  # 反転後、次の6ビットは反転禁止
            else:
                result.append(bit)

    introduced_errors_data = ''.join(result)

    # 空白を含む形式にフォーマット
    encoded_data_spaced = format_binary_string(encoded_data, 7)
    introduced_errors_data_spaced = format_binary_string(introduced_errors_data, 7)

    # 色付けされた文字列を作成
    trans_data_colored = ''.join([
        print_color(bit, 'red') if encoded_data_spaced[i] != introduced_errors_data_spaced[i] else bit
        for i, bit in enumerate(introduced_errors_data_spaced)
    ])

    print()
    print("雑音のある通信路")
    print(f"Transmitted    : {trans_data_colored}")
    return introduced_errors_data

def save_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(data)

def save_codebook(filename, codebook):
    with open(filename, 'w') as file:
        json.dump(codebook, file)

def load_codebook(filename):
    with open(filename, 'r') as file:
        codebook = json.load(file)
    return codebook

def save_padding_length(filename, padding_length):
    with open(filename, 'w') as file:
        file.write(str(padding_length))

def load_padding_length(filename):
    with open(filename, 'r') as file:
        padding_length = int(file.read())
    return padding_length

def load_from_file(filename, orig, other):
    if not os.path.exists(filename):
        print(f"{other} さんから {orig} さんへのメッセージはありません。")
        return None
    with open(filename, 'r') as file:
        data = file.read()
    return data

def receive_message(codebook_filename, padding_filename, data_filename, message_from, message_to):
    try:
        codebook = load_codebook(codebook_filename)
        padding_length = load_padding_length(padding_filename)
        received_data = load_from_file(data_filename, message_from, message_to)
    except Exception as exc:
        print("エラー：", str(exc))
        print(f"{message_from} さんから {message_to} さんへ既にメッセージが送信されたかどうか確認して下さい")

    return codebook, padding_length, received_data

def send_message(saved_dir, message_from, message_to, encoded_data, codebook, padding_length, error_rate=0.2):
    transmitted_data = introduce_errors(encoded_data, error_rate)
    # ファイル名設定
    data_filename = f"{saved_dir}/{message_from}-{message_to}.txt"
    codebook_filename = f"{saved_dir}/{message_from}-{message_to}-codebook.json"
    padding_filename = f"{saved_dir}/{message_from}-{message_to}-padding.txt"

    save_to_file(data_filename, transmitted_data)
    save_codebook(codebook_filename, codebook)
    save_padding_length(padding_filename, padding_length)
