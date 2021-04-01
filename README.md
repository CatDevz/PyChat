## PyChat is a Chat Application & Protocol implemented in Python

---

When a packet is sent it is formatted in the following.

- [4 Byte] Header containing packet length
- [PACKET_LENGTH] UTF-8 encoded JSON string containing information

The JSON is always formatted in the following:

```json
// (this is 1 example of a message type packet, only the type & data fields are required and the expected structure of the data field will change depending on the type field defined)

{
    "type": "message" /* JSON String containing packet type */,
    "data": {
        // JSON Object containing packet contents
        "body": "This is my first message!",
        "author": "Cody",
        "color": "RED",
    }
}
```

Any malformed packets will be ignored

---

Licensed under GNU GPL 3 license. You are free to fork, modify, and redistrubute at your will.