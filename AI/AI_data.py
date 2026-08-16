STRATEGIA_HIHAVAKIO = {
    "panostus1": {  #ennen vaihtoja
        "pari": {
            "call": 0.5,
            "raise": 0.3,
            "fold": 0.2
        }
    },
    "panostus2": { #vaihtojen jälkeen
        "pari": {
            "call": 0.5,
            "raise": 0.15,
            "fold": 0.35
        }

    }  
}


STRATEGIA_VAHVISTUSOPPI = {
    ("panostus1", "pari", "high", 3): {
        "call": 0.55,
        "raise": 0.35,
        "fold": 0.10
    }
}

#määrittele tila jotenkin: (kierros, käsivahvuus, stack, pot, pelaajiamukana...)