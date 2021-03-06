
class FAIL_REASON:
    SUCCESS = 0
    QUEUE_FULL = 1
    MISSING_LEADER = 2
    DISCARDED = 3
    NOT_LEADER = 4
    LEADER_CHANGED = 5

class SERIALIZER_STATE:
    NOT_SERIALIZING = 0     # Serialization not started or already finished.
    SERIALIZING = 1         # Serialization in progress.
    SUCCESS = 2             # Serialization successfully finished (should be returned only one time after finished).
    FAILED = 3              # Serialization failed (should be returned only one time after finished).

class SyncObjConf(object):
    def __init__(self, **kwargs):

        # Encrypt session with specified password.
        # Install 'cryptography' module to be able to set password.
        self.password = kwargs.get('password', None)

        # Disable autoTick if you want to call onTick manually.
        # Otherwise it will be called automatically from separate thread.
        self.autoTick = kwargs.get('autoTick', True)
        self.autoTickPeriod = kwargs.get('autoTickPeriod', 0.05)

        # Commands queue is used to store commands before real processing.
        self.commandsQueueSize = kwargs.get('commandsQueueSize', 100000)

        # After randomly selected timeout (in range from minTimeout to maxTimeout)
        # leader considered dead, and leader election starts.
        self.raftMinTimeout = kwargs.get('raftMinTimeout', 0.4)
        self.raftMaxTimeout = kwargs.get('raftMaxTimeout', 1.4)

        # Interval of sending append_entries (ping) command.
        # Should be less then raftMinTimeout.
        self.appendEntriesPeriod = kwargs.get('appendEntriesPeriod', 0.1)

        # When no data received for connectionTimeout - connection considered dead.
        # Should be more then raftMaxTimeout.
        self.connectionTimeout = kwargs.get('connectionTimeout', 3.5)

        # Interval between connection attempts.
        # Will try to connect to offline nodes each connectionRetryTime.
        self.connectionRetryTime = kwargs.get('connectionRetryTime', 5.0)

        # Send multiple entries in a single command.
        # Enabled (default) - improve overall performance (requests per second)
        # Disabled - improve single request speed (don't wait till batch ready)
        self.appendEntriesUseBatch = kwargs.get('appendEntriesUseBatch', True)

        # Max number of bytes per single append_entries command.
        self.appendEntriesBatchSizeBytes = kwargs.get('appendEntriesBatchSizeBytes', 2 ** 16)

        # Size of receive and send buffer for sockets.
        self.sendBufferSize = kwargs.get('sendBufferSize', 2 ** 16)
        self.recvBufferSize = kwargs.get('recvBufferSize', 2 ** 16)

        # Time to cache dns requests (improves performance,
        # no need to resolve address for each connection attempt).
        self.dnsCacheTime = kwargs.get('dnsCacheTime', 600.0)
        self.dnsFailCacheTime = kwargs.get('dnsFailCacheTime', 30.0)

        # Log will be compacted after it reach minEntries size or
        # minTime after previous compaction.
        self.logCompactionMinEntries = kwargs.get('logCompactionMinEntries', 5000)
        self.logCompactionMinTime = kwargs.get('logCompactionMinTime', 300)

        # If true - each node will start log compaction in separate time window.
        # eg. node1 in 12.00-12.10, node2 in 12.10-12.20, node3 12.20 - 12.30,
        # then again node1 12.30-12.40, node2 12.40-12.50, etc.
        self.logCompactionSplit = kwargs.get('logCompactionSplit', False)

        # Max number of bytes per single append_entries command
        # while sending serialized object.
        self.logCompactionBatchSize = kwargs.get('logCompactionBatchSize', 2 ** 16)

        # If true - commands will be enqueued and executed after leader detected.
        # Otherwise - FAIL_REASON.MISSING_LEADER error will be emitted.
        # Leader is missing when esteblishing connection or when election in progress.
        self.commandsWaitLeader = kwargs.get('commandsWaitLeader', True)

        # File to store full serialized object. Save full dump on disc when doing log compaction.
        # None - to disable store.
        self.fullDumpFile = kwargs.get('fullDumpFile', None)

        # File to store operations journal. Save each record as soon as received.
        self.journalFile = kwargs.get('journalFile', None)

        # Will try to bind port every bindRetryTime seconds until success.
        self.bindRetryTime = kwargs.get('bindRetryTime', 1.0)

        # This callback will be called as soon as SyncObj sync all data from leader.
        self.onReady = kwargs.get('onReady', None)

        # If enabled - cluster configuration could be changed dynamically.
        self.dynamicMembershipChange = kwargs.get('dynamicMembershipChange', False)

        # Sockets poller:
        #  'auto' - auto select best available on current platform
        #  'select' - use select poller
        #  'poll' - use poll poller
        self.pollerType = kwargs.get('pollerType', 'auto')

        # Use fork if available when serializing on disk.
        self.useFork = kwargs.get('useFork', True)

        # Custom serialize function, it will be called when logCompaction (fullDump) happens.
        # If specified - there should be a custom deserializer too.
        # Arguments: serializer(fileName, data)
        #  data - some internal stuff that is *required* to be serialized with your object data.
        self.serializer = kwargs.get('serializer', None)

        # Check custom serialization state, for async serializer.
        # Should return one of SERIALIZER_STATE.
        self.serializeChecker = kwargs.get('serializeChecker', None)

        # Custom deserialize function, it will be called when restore from fullDump.
        # If specified - there should be a custom serializer too.
        # Should return data - internal stuff that was passed to serialize.
        self.deserializer = kwargs.get('deserializer', None)

    def validate(self):
        assert self.autoTickPeriod > 0
        assert self.commandsQueueSize >= 0
        assert self.raftMinTimeout > self.appendEntriesPeriod * 3
        assert self.raftMaxTimeout > self.raftMinTimeout
        assert self.appendEntriesPeriod > 0
        assert self.connectionTimeout >= self.raftMaxTimeout
        assert self.connectionRetryTime >= 0
        assert self.appendEntriesBatchSizeBytes > 0
        assert self.sendBufferSize > 0
        assert self.recvBufferSize > 0
        assert self.dnsCacheTime>= 0
        assert self.dnsFailCacheTime >= 0
        assert self.logCompactionMinEntries >= 2
        assert self.logCompactionMinTime > 0
        assert self.logCompactionBatchSize > 0
        assert self.bindRetryTime > 0
        assert (self.deserializer is None) == (self.serializer is None)
        if self.serializer is not None:
            assert self.fullDumpFile is not None
