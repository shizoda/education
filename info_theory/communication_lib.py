import numpy as np
from collections import Counter
import pandas as pd
import graphviz
from IPython.display import Image, display
import random
import os
import json

# ユーティリティ関数
color_dic = {"black":"\033[30m", "red":"\033[31m", "green":"\033[32m", "yellow":"\033[33m", "blue":"\033[34m", "end":"\033[0m"}

def print_color(text, color="red"):
    return color_dic[color] + text + color_dic["end"]

def format_binary_string(binary_string, chunk_size=7, max_length=50):
    if len(binary_string) > max_length:
        binary_string = binary_string[:max_length] + "..."
    formatted_string = ' '.join([binary_string[i:i+chunk_size] for i in range(0, len(binary_string), chunk_size)])
    return formatted_string

# 行列を定義
# 生成行列 G (データビット → コードワード)
G = np.array([
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 0, 1, 1],
    [0, 0, 1, 0, 1, 0, 1],
    [0, 0, 0, 1, 1, 1, 1]
])

# 検査行列 H (シンドローム計算用)
H = np.array([
    [1, 0, 1, 1, 1, 0, 0],
    [1, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1]
])

def hamming_encode(data):
    """
    行列計算を用いてハミングコードを生成する（後ろ3ビットがパリティビット）
    """
    print(f"Hamming Input  : {format_binary_string(data, 4)}")
    
    encoded_data = []
    for i in range(0, len(data), 4):
        # 4ビットのデータブロックを取得
        block = data[i:i+4]
        if len(block) < 4:
            block = block + '0' * (4 - len(block))  # 足りない分は0でパディング
        
        # 整数配列に変換
        data_bits = np.array([int(bit) for bit in block])
        
        # 生成行列Gを使って符号化（行列の積を計算し、mod 2を適用）
        encoded_bits = np.dot(data_bits, G) % 2
        
        # 結果を追加
        encoded_data.extend(encoded_bits)
    
    encoded_str = ''.join(map(str, encoded_data))
    
    # 表示用のフォーマット（データビットとパリティビットを色分け）
    formatted_encoded_str = format_binary_string(encoded_str, 7)
    formatted_encoded_str = ''.join([print_color(bit, 'blue') if i % 7 in [4, 5, 6] else bit for i, bit in enumerate(formatted_encoded_str.replace(" ", ""))])
    
    print(f"Hamming Encoded: {formatted_encoded_str}")
    return encoded_str

def hamming_decode(data):
    """
    行列計算を用いてハミングコードをデコードする（後ろ3ビットがパリティビット）
    """
    decoded_data = []
    decoded_data_all = []
    n_corrected = 0
    corrected_blocks = []
    
    for i in range(0, len(data), 7):
        # 7ビットのブロックを取得
        block = data[i:i+7]
        if len(block) < 7:
            block = block + '0' * (7 - len(block))  # 足りない分は0でパディング
        
        # 整数配列に変換
        received_bits = np.array([int(bit) for bit in block])
        
        # 検査行列Hを使ってシンドロームを計算
        syndrome = np.dot(H, received_bits) % 2
        
        # シンドロームを整数に変換
        error_position = syndrome[0] * 1 + syndrome[1] * 2 + syndrome[2] * 4
        
        # 元のブロックを保存
        original_block = ''.join(map(str, received_bits))
        
        # エラーがあれば訂正
        corrected_bits = received_bits.copy()
        if error_position > 0:
            # エラー位置を計算（行列Hの列との一致を見る）
            for j in range(7):
                h_column = H[:, j]
                if np.array_equal(h_column, syndrome):
                    corrected_bits[j] ^= 1  # エラービットを反転
                    if n_corrected < 10:
                        corrected_blocks.append((i, j, original_block, ''.join(map(str, corrected_bits))))
                    n_corrected += 1
                    break
        
        # データビットのみを抽出（最初の4ビット）
        decoded_block = corrected_bits[:4]
        decoded_data.extend(decoded_block)
        decoded_data_all.extend(corrected_bits)
    
    # 結果を文字列に変換
    decoded_str = ''.join(map(str, decoded_data))
    decoded_str_all = ''.join(map(str, decoded_data_all))
    
    # 訂正されたブロックを表示
    print(f"{n_corrected} corrections in total.")
    for i, error_position, original, corrected in corrected_blocks:
        print(f"  (Block-{i//7}, Bit-{error_position}): {format_binary_string(original)} --> {format_binary_string(corrected)}")
    if n_corrected > 10:
        print("      etc.")
    
    # フォーマットして表示
    formatted_data = format_binary_string(data, 7)
    formatted_data = ''.join([print_color(bit, 'blue') if i % 7 in [4, 5, 6] else bit for i, bit in enumerate(formatted_data.replace(" ", ""))])
    
    formatted_decoded_str_all = format_binary_string(decoded_str_all, 7)
    formatted_decoded_str_all = ''.join([print_color(bit, 'blue') if i % 7 in [4, 5, 6] else bit for i, bit in enumerate(formatted_decoded_str_all.replace(" ", ""))])
    
    formatted_decoded_str = format_binary_string(decoded_str, 4)
    
    print("Received       :", formatted_data)
    print("Hamming Decoded:", formatted_decoded_str_all)
    print("Hamming Output :", formatted_decoded_str)
    return decoded_str

def introduce_errors(encoded_data, error_rate):
    """
    ランダムにビットエラーを導入する
    """
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

# その他の関数はオリジナルのままで良い（Huffman関連の関数など）
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