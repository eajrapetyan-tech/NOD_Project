from save_history.collectors import TwoGisCountCollector, VisitPetersburgPlacesCollector


def test_2gis_places_count_parser():
    text = "Рестораны СПб Фильтры Места 4105 По рейтингу"
    assert TwoGisCountCollector._extract_places_count(text) == 4105


def test_visit_petersburg_name_address_split():
    parsed = VisitPetersburgPlacesCollector._split_name_address("Исаакиевский Собор Исаакиевская пл., 4")
    assert parsed == ("Исаакиевский Собор", "Исаакиевская пл., 4")


def test_visit_petersburg_multiword_names_do_not_leak_into_address():
    cases = [
        (
            "Музей антропологии и этнографии им. Петра Великого Российской академии наук | "
            "Кунсткамера Университетская наб., 3",
            (
                "Музей антропологии и этнографии им. Петра Великого Российской академии наук | Кунсткамера",
                "Университетская наб., 3",
            ),
        ),
        ("Лахта Центр Высотная ул., 1", ("Лахта Центр", "Высотная ул., 1")),
        (
            "Санкт-Петербургский Государственный Университет | Здание двенадцати коллегий "
            "Университетская наб., 7-9",
            (
                "Санкт-Петербургский Государственный Университет | Здание двенадцати коллегий",
                "Университетская наб., 7-9",
            ),
        ),
    ]

    for text, expected in cases:
        assert VisitPetersburgPlacesCollector._split_name_address(text) == expected
