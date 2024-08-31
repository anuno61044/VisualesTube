from rest_framework import generics
from .models import Movie, Rating, User
from .serializers import MovieSerializer, RatingSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .recommender import get_recommendations  # función que debes crear

class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class UserRecommendations(APIView):
    def get(self, request, user_id):
        recommendations, trace = get_recommendations(user_id)
        serialized_recommendations = MovieSerializer(recommendations, many=True).data
        return Response({
            "recommendations": serialized_recommendations,
            "trace": trace
        })

@api_view(['POST'])
def rate_movie(request, movie_id):
    user_id = request.data.get('user_id')
    score = request.data.get('score')
    
    movie = Movie.objects.get(id=movie_id)
    user = User.objects.get(id=user_id)

    # Actualizar o crear la calificación
    rating, created = Rating.objects.update_or_create(
        user=user,
        movie=movie,
        defaults={'score': score}
    )

    return Response({"success": True, "rating": rating.score})


class UserRatingsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        ratings = Rating.objects.filter(user=user).select_related('movie')
        rated_movies = [
            {
                "movie_id": rating.movie.id,
                "score": rating.score
            }
            for rating in ratings
        ]

        return Response({
            "user": user.username,
            "rated_movies": rated_movies
        })
    

class UsersRatingsView(APIView):
    def get(self, request):
        user_ids = request.query_params.getlist('user_ids')
        if not user_ids:
            return Response({"error": "No user IDs provided"}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(id__in=user_ids)

        if not users.exists():
            return Response({"error": "No valid users found"}, status=status.HTTP_404_NOT_FOUND)

        # Obtener todas las películas calificadas por al menos uno de los usuarios
        all_movies = Movie.objects.filter(rating__user__in=users).distinct()

        result = []
        for movie in all_movies:
            movie_ratings = {"movie_title": movie.title}
            for user in users:
                rating = Rating.objects.filter(user=user, movie=movie).first()
                movie_ratings[str(user.id)] = rating.score if rating else 0
            result.append(movie_ratings)

        return Response(result)