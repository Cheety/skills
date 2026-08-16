from dataclasses import dataclass


@dataclass          # !! IMMUTABILITY_DTO
class PostenData:
    quantity: int
