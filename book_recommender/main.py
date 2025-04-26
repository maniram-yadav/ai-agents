from book_recommender import BookRecommender

recommender = BookRecommender()
print("Welcome to the Personalized Book Recommendation System!")
print("Tell me about your favorite books, authors, or genres.")
print("Example: 'I love fantasy novels like Lord of the Rings and sci-fi by Isaac Asimov'")
print("Type 'quit' to exit.\n")

while True:
    user_input = input("Your reading preferences : ")
    if user_input.lower()=='quit':
        break
    recommendation = recommender.get_recommendations(user_input)
    print("\nHere are some books you might enjoy: \n")
    print(recommendation)
    print("\n")