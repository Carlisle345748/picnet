import boto3
from cachetools import cached, TTLCache
from graphene import String, List, ObjectType, Int

cognito_client = boto3.client('cognito-identity', region_name="us-west-2")
credential = cognito_client.get_credentials_for_identity(
    IdentityId='us-west-2:00a9c5a6-1b98-432c-a718-482c41436bf6'
)

location_client = boto3.client('location',
                               region_name="us-west-2",
                               aws_access_key_id=credential['Credentials']['AccessKeyId'],
                               aws_secret_access_key=credential['Credentials']['SecretKey'],
                               aws_session_token=credential['Credentials']['SessionToken'])


class Location(ObjectType):
    full_address = String()
    main = String()
    secondary = String()


@cached(cache=TTLCache(maxsize=4096, ttl=86400))
def get_suggestion(text, top_n):
    result: dict = location_client.search_place_index_for_suggestions(
        IndexName='PhotoShareApp',
        MaxResults=top_n,
        Text=text
    )
    return [place['Text'] for place in result["Results"]]


def parse_address(address: str) -> Location:
    parts = address.split(',', maxsplit=1)
    main = parts[0]
    secondary = parts[1].strip() if len(parts) == 2 else ""
    return Location(main=main, secondary=secondary, full_address=address)


class AWSQuery(ObjectType):
    location_suggestions = List(Location, text=String(), top_n=Int(default_value=5))

    def resolve_location_suggestions(self, info, text, top_n):
        addresses = get_suggestion(text, top_n)
        return [parse_address(a) for a in addresses]
