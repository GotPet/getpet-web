import json

from getpet import settings


class Constants(object):
    GETPET_ORGANIZATION_JSON_LD = json.dumps({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "GetPet",
        "legalName": "Augink mane, VšĮ",
        "url": "https://www.getpet.lt/",
        "telephone": settings.CONTACT_PHONE,
        "email": settings.EMAIL_TO,
        "logo": "https://www.getpet.lt/static/web/img/logo/getpet-logo-square-big.png",
        "foundingDate": "2018",
        "founders": [
            {
                "@type": "Person",
                "name": "Karolis Vyčius"
            },
            {
                "@type": "Person",
                "name": "Rūta Langaitė"
            },
            {
                "@type": "Person",
                "name": "Vaidas Gecevičius"
            },
            {
                "@type": "Person",
                "name": "Asta Zaiceva Stalmakova"
            }
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": settings.CONTACT_PHONE,
            "email": settings.EMAIL_TO,
            "availableLanguage": [
                {
                    "@type": "Language",
                    "name": "Lithuanian"
                },
                {
                    "@type": "Language",
                    "name": "English"
                }
            ]
        },
        "sameAs": [
            "https://www.facebook.com/getpet.lt",
            "https://www.instagram.com/getpet.lt/",
            "https://www.linkedin.com/company/getpet/",
            "https://apps.apple.com/lt/app/getpet/id1450751703",
            "https://play.google.com/store/apps/details?id=lt.getpet.getpet&hl=lt&pcampaignid=web"
        ]
    })
