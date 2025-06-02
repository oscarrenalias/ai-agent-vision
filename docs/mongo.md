# Working with MongoDB

# Using Mongosh

## DevContainer

`mongosh` is available out of the box in the DevContainer. It will automatically connect to the local mongo instance.

## Using Mongo Docker image

For troubleshooting purposes, it possible to run mongosh from inside the mongo container that docker-compose deploys:

```sh
docker-compose -f docker-compose.release.yml run mongo mongosh mongodb://mongo:27017

```

# Replica Set

Mongo is configured as a replica set so that we can use change streams to automatically recalculate analytics data when it changes. Technically replica sets are used for replicating data cross mongo servers, but we only deploy mongo as a single host.

To check that replica set is configured, use this mongosh:

```
rs.conf()
```

It should produce output like this:

```json
{
  _id: 'rs0',
  version: 1,
  term: 7,
  members: [
    {
      _id: 0,
      host: 'mongodb:27017',
      arbiterOnly: false,
      buildIndexes: true,
      hidden: false,
      priority: 1,
      tags: {},
      secondaryDelaySecs: Long('0'),
      votes: 1
    }
  ],
  protocolVersion: Long('1'),
  writeConcernMajorityJournalDefault: true,
  settings: {
    chainingAllowed: true,
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {},
    getLastErrorDefaults: { w: 1, wtimeout: 0 },
    replicaSetId: ObjectId('682b7ae7906615702e2fc916')
  }
}
```

The replica set is enabled out of the box when using the default docker-compose.release.yml file.
