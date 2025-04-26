from book_recommender import BookRecommender
from buffered_book_recommender import BufferedBookRecommender


recommender = BookRecommender()
buffered_recommender = BufferedBookRecommender()
print("Welcome to the Personalized Book Recommendation System!")
print("Tell me about your favorite books, authors, or genres.")
print("Example: 'I love fantasy novels like Lord of the Rings and sci-fi by Isaac Asimov'")
print("Type 'quit' to exit.\n")
user_input = input("BookRecommender Model Prefernce : memory/simple : ")
if not(user_input=='memory' or user_input=='simple') :
    print("Invalid input provided")
    raise "Invalid input"

while True:
    user_input = input("Your reading preferences : ")
    if user_input.lower()=='quit':
        break
    recommendation = None
    if user_input.lower()=='memory':
        recommendation = buffered_recommender.chat(user_input)
    elif user_input.lower()=='simple':
        recommendation = recommender.get_recommendations(user_input)
    
    print("\nHere are some books you might enjoy: \n")
    print(recommendation)
    print("\n")