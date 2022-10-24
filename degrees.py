import csv
import sys

from util import Node, StackFrontier, QueueFrontier

"""TESTJPF
The new algorithm, called expected value navigation (EVN), works by always passing a message to the node that has the highest probability of linking to the target. The probability is calculated from the number of links the next potential node boasts – or its “degree” – and from its similarity, or “homophily”, to the target.

Could be greeedy, but not a*?!?!?:::
sort by  WITH MOST NEIGHBORS, Large amount of neighbors, means each on eis UNIQUE (at first, but still most likely to be unique)
sort by amount of neighbors
flatten
then remove dupes
"""

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(actorA, actorZ):
    """
    @state: ID that can be CRUDed from frontier
    """
    startZ = Node(state=(actorZ, "z"), parent=None, action=(None, None))
    startA = Node(state=(actorA, "a"), parent=None, action=(None, None))
    actions = []
    num_explored = 0
    frontier = QueueFrontier()
    explored = set()
    solver = None

    frontier.add(startZ)
    frontier.add(startA)

    while solver == None:
        # If nothing left in frontier, then no path
        if frontier.empty():
            print("nodes explored: ", num_explored)
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        num_explored += 1

        print("fart", node.state[0])
        neighbors = neighbors_for_person(node.state[0])
        print("fart222")
        if node.state[1] == "a":
            target = actorZ
        else:
            target = actorA

        tempNeighbors = []

        explored.add(node.state[0])
        for neighbor in neighbors:
            if neighbor[1] == target:
                if node.state[1] == "z":
                    actions.append((neighbor[0], node.state[0]))
                else:
                    actions.append(neighbor)
                while node.parent is not None:
                    if node.state[1] == "z":
                        actions.append((node.action[0], node.parent.state[0]))
                    else:
                        actions.append(node.action)
                    node = node.parent
                solver = node.state[1]
                break
            else:
                tempNeighbors.append(neighbor)

        flatNoDupes = list(
            set([item for sublist in tempNeighbors for item in sublist]))

        print(flatNoDupes)

        for neighbor in flatNoDupes:
            if not frontier.contains_state(neighbor[1]) and neighbor[1] not in explored:
                child = Node(state=(neighbor[1], node.state[1]),
                             parent=node, action=neighbor)
                frontier.add(child)

        tempNeighbors.clear()

    print("nodes explored: ", num_explored)
    print("solver: ", solver)
    if solver == "a":
        actions.reverse()

    """
    need to return in this format:
    [(1, 2), (3, 4)], that would mean that the source starred in movie 1 with person 2, person 2 starred in movie 3 with person 4, and person 4 is the target.
    """

    return actions


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
