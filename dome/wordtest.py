import random

# 假设words是一个包含所有100个单词的列表
# 每个单词对应一个权重，例如 [(word1, 200), (word2, 100), ..., (word100, 50)]
words_with_weights = [("word" + str(i), weight) for i, weight in enumerate([200]*10 + [100]*20 + [50]*70)]

def weighted_random_selection(words_with_weights, num_selections=10):
    selected_words = []
    for _ in range(num_selections):
        total_weight = sum(weight for _, weight in words_with_weights)
        r = random.uniform(0, total_weight)
        upto = 0
        for word, weight in words_with_weights:
            if upto + weight >= r:
                selected_words.append(word)
                break
            upto += weight
    return selected_words

# 获取10个单词
selected_words = weighted_random_selection(words_with_weights)
print(selected_words)
