# Analyse de données

## 1. Combien d’images, de boîtes, de classes ? Sont-elles équilibrées ?
Images trouvées : 1800
Boîtes : 4189
classes : 6
Non, elles ne sont pas équilibrées.

classe
inclusion          1011
patches             881
crazing             689
rolled-in_scale     628
scratches           548
pitted_surface      432

## 2. Quels défauts sont les plus petits (médiane de aire_rel) ? Donc les plus difficiles.
Les defauts les plus petits sont les patches

## 3. La luminosité moyenne diffère-t-elle d’une classe à l’autre ?
Oui, la luminosité moyenne différe d'une classe à une autre.
                  mean
classe                      
crazing          141.1  
inclusion        106.4  
patches          132.5  
pitted_surface   176.7  
rolled-in_scale  117.9  
scratches         95.1

## 4. Quelles classes se ressemblent sur exemples.png ? 
Les classes qui se ressemble sont : les inclusions, crazing et rolled-in_scale.