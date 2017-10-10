import json

def test_create_bucketlist(client):
    """
    Test API can create a bucketlist (POST request)
    """
    # mock data
    bucketlist = {'name': 'Career'}

    response = client.post('/bucketlists/', data=bucketlist)
    assert response.status_code == 201
    assert 'Career' in response.data
