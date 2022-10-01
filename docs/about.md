# About

## What is it?

**Stubborn** is a free and open-source web application providing a virtual API stub service for testing and development purposes.

API stub methods might be handy in mocking the third-party API services. So, the main idea is to provide a minimal
implementation of an interface that allows the developer or tester to set up an API method that returns hardcoded
(and partly generated) data tightly coupled to the test suite. Also, it must be easy to share the stub with
teammates and (or) use it permanently with the staging instance of the main application.

## Features

- Customizable mocking web resources.
- JSON, XML, Text request/response body formats support.
- Customizable response timeout support.
- Customizable event-based webhooks call support.
- Logging containing exhaustive request & response data.

## Common usage scenarios

- mock of the third-party service for QA and backend development
- flexible mock of the backend service for QA and frontend development
- service-in-the-middle for debugging and testing purpose

In every case of usage Stubborn will save and provide exhaustive data about received requests and responses sent.

## Supported platforms

- linux/amd64
- linux/arm64/v8
- linux/arm32/v7 *(Yes! You can run it on your Raspberry Pi!)*

## Hardware requirements

- **Minimum:** 1 CPU, 0.5 GiB memory. The low-end and cheapest `t4g.nano` AWS instance (ARM64) works fine but runs at 80-90% memory utilization.
- **Recommended:** 1-2 CPU, 1 GiB memory. In general, hardware requirements directly depend on the service load. In the case of intensive use of the Stubborn by several teams, it's recommended to increase the CPU number to at least two.
