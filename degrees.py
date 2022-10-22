import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}
# tracker testjpf


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


def same_movie(neighbors, target):
    """
    testjpf
    tom hanks (source) = 158
    sally field (target) = 398
    forest gump (targets movie) = 109830
    """

    # see if taget is in neighbors.
    # neighbors
    print(target)
    for neighbor in neighbors:
        print(neighbor[1])
        if neighbor[1] == target:
            """
            need to return in a format like:
            [(1, 2), (3, 4)], that would mean that the source starred in movie 1 with person 2, person 2 starred in movie 3 with person 4, and person 4 is the target.

            my EX: [(109830,398)]
            """
            return neighbor
    return (-1, -1)


def shortest_path(actorA, actorZ):
    actions = []
    solution = []
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.

    testjpf

    first logical step is to see if they've been in a movie together

    """
    # Keep track of number of states explored
    num_explored = 0

    """
    what is my start.state? TESTJPF
    source? Ex: Tom Hanks SOURCE NEIGHBORS?!!?!
    """

    # Initialize frontier to just the starting position
    """
    state could be true or false?testjpf
    state is true they star in a movie actorZ or false
    """
    sourceNeighbors = neighbors_for_person(actorA)
    starTogether = same_movie(sourceNeighbors, actorZ)
    print(starTogether)
    if starTogether[1] == actorZ:
        print("STARTOGETHER")
        actions.append(starTogether)
    start = Node(state=actorA, parent=None, action=starTogether)

    """
    loop thru neighbors check to see if it solves, if not create a node for it and add source as parent
    """
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    solved = False

    while solved == False:
        # If nothing left in frontier, then no path
        if frontier.empty():
            raise Exception("no solution")

        # Choose a node from the frontier
        node = frontier.remove()
        num_explored += 1

        if node.action[1] == actorZ:
            print(actions)
            """
            steal from maze.py ln: 145 testjpf
            """

            while node.parent is not None:
                actions.append(node.action)
                node = node.parent
            solved = True
        else:
            # Add neighbors to frontier
            """
            what is my action?!?!? TESTJPF
            action = [Movie_id, (starred with) person_id]
            """
            sourceNeighbors = neighbors_for_person(node.state)
            for neighbor in sourceNeighbors:
                # this conditional is where you'd check to see if ylu already know that this neighbor hasn't starred in a movie with actorZ
                if not frontier.contains_state(node.state) and node.state not in explored:
                    child = Node(state=neighbor[1],
                                 parent=node, action=neighbor)
                    frontier.add(child)
    actions.reverse()
    print("action reverse")
    print(actions)
    if actions[0] != -1:
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
