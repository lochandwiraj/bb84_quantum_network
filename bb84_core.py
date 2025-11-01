import random

def generate_bits(n):
    return [random.randint(0, 1) for _ in range(n)]

def generate_bases(n):
    return [random.choice(['X', 'Z']) for _ in range(n)]

def measure(bits, bases, measurement_bases):
    measured = []
    for bit, base, m_base in zip(bits, bases, measurement_bases):
        if base == m_base:
            measured.append(bit)
        else:
            measured.append(random.randint(0, 1))
    return measured

def sift_keys(sender_bases, receiver_bases, sender_bits, receiver_bits):
    shared_bits = [b for b, sb, rb in zip(sender_bits, sender_bases, receiver_bases) if sb == rb]
    receiver_shared_bits = [r for r, sb, rb in zip(receiver_bits, sender_bases, receiver_bases) if sb == rb]
    return shared_bits, receiver_shared_bits
