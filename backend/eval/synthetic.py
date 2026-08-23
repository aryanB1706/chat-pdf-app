"""Synthetic multi-page corpus with distinctive per-page facts.

Used by the offline eval so it runs with zero deps (no DB, no API key).
Each page has unique keywords; eval questions target exactly one page
(or two pages for compare questions).
"""

PAGES: list[str] = [
    # Page 1
    "Photosynthesis occurs in chloroplasts where chlorophyll captures sunlight. "
    "The light reactions produce ATP and NADPH for the Calvin cycle. "
    "Stomata regulate gas exchange during photosynthesis.",
    # Page 2
    "Mitochondria generate ATP through cellular respiration. "
    "The Krebs cycle runs in the mitochondrial matrix. "
    "Oxidative phosphorylation happens across the inner membrane.",
    # Page 3
    "Newton's second law states force equals mass times acceleration. "
    "Inertia keeps objects moving at constant velocity without net force. "
    "Action and reaction forces are equal and opposite.",
    # Page 4
    "The water cycle moves water through evaporation and condensation. "
    "Transpiration from plants adds moisture to the atmosphere. "
    "Precipitation returns water to oceans and aquifers.",
    # Page 5
    "Machine learning trains models by minimizing a loss function. "
    "Gradient descent updates weights using backpropagation. "
    "Overfitting is controlled with regularization and validation splits.",
    # Page 6
    "Databases use B-tree indexes to speed up range queries. "
    "ACID transactions guarantee atomicity and durability. "
    "Normalization reduces redundancy across tables.",
    # Page 7
    "The French Revolution began in 1789 with the storming of the Bastille. "
    "The Declaration of the Rights of Man asserted liberty and equality. "
    "Napoleon rose to power after the Directory collapsed.",
    # Page 8
    "Quantum mechanics describes particles with wave functions. "
    "The Heisenberg uncertainty principle limits position and momentum precision. "
    "Superposition collapses upon measurement.",
    # Page 9
    "Supply and demand set equilibrium prices in markets. "
    "Inflation erodes purchasing power when money supply grows fast. "
    "Central banks adjust interest rates to stabilize growth.",
    # Page 10
    "TCP provides reliable ordered delivery with retransmissions. "
    "UDP is connectionless and suits low-latency streaming. "
    "DNS resolves domain names to IP addresses.",
]
