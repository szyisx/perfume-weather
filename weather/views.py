from django.shortcuts import render

from .services import OpenMeteoClient, PerfumeRecommender, WeatherError


def recommend_view(request):
    city = (request.GET.get("city") or "").strip()
    if not city:
        return render(request, "weather/recommend.html", {"city": ""})

    client = OpenMeteoClient()
    recommender = PerfumeRecommender()

    try:
        snapshot = client.fetch_snapshot(city)
    except WeatherError as exc:
        return render(
            request,
            "weather/recommend.html",
            {"city": city, "error": str(exc)},
        )

    perfumes, families = recommender.recommend(snapshot)

    return render(
        request,
        "weather/recommend.html",
        {
            "city": city,
            "snapshot": snapshot,
            "perfumes": perfumes,
            "matched_families": families,
        },
    )
